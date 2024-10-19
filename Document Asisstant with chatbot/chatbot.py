# chatbot.py

import os
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatOpenAI
from qdrant_client import QdrantClient
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
import streamlit as st
from streamlit_callback_handler import StreamlitCallbackHandler

class ChatbotManager:
    def __init__(   
        self,
        model_name: str = "BAAI/bge-m3",
        device: str = "cpu",
        encode_kwargs: dict = {"normalize_embeddings": True},
        llm_choice: str = "ollama",
        llm_model: str = "llama3.2:3b",
        llm_temperature: float = 0,
        openai_api_key: str = None,
        openai_model: str = "gpt-3.5-turbo",
        openai_temperature: float = 0,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "Rishabh_Collection",
    ):
        self.model_name = model_name
        self.device = device
        self.encode_kwargs = encode_kwargs
        self.llm_choice = llm_choice
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.openai_temperature = openai_temperature
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name

        # Initialize Embeddings
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": self.device},
            encode_kwargs=self.encode_kwargs,
        )

        # Initialize LLM based on choice
        self.initialize_llm()

        # Define the prompt template
        self.prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer. Answer must be detailed and well explained.
Helpful answer:
"""

        # Initialize Qdrant client
        self.client = QdrantClient(
            url=self.qdrant_url, prefer_grpc=False
        )

        # Initialize the Qdrant vector store
        self.db = Qdrant(
            client=self.client,
            embeddings=self.embeddings,
            collection_name=self.collection_name
        )

        # Initialize the prompt
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=['context', 'question']
        )

        # Initialize the retriever
        self.retriever = self.db.as_retriever(search_kwargs={"k": 10})

        # Define chain type kwargs
        self.chain_type_kwargs = {"prompt": self.prompt}

        # Initialize the RetrievalQA chain
        self.initialize_qa_chain()

    def initialize_llm(self):
        streamlit_container = st.empty()
        callback_handler = StreamlitCallbackHandler(container=streamlit_container)

        if self.llm_choice == "ollama":
            self.llm = ChatOllama(
                model=self.llm_model,
                temperature=self.llm_temperature,
                streaming=True,
                callbacks=[callback_handler],
            )
        elif self.llm_choice == "openai":
            self.llm = ChatOpenAI(
                model=self.openai_model,
                temperature=self.openai_temperature,
                api_key=self.openai_api_key,
                callbacks=[callback_handler],
            )
        else:
            raise ValueError(f"Unsupported LLM choice: {self.llm_choice}")

    def initialize_qa_chain(self):
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=False,  # Set to False to not return source documents
            chain_type_kwargs=self.chain_type_kwargs,
            verbose=False
        )

    def get_response(self, query: str) -> str:
            try:
                response = self.qa(query)
                answer = response['result']
                return answer  # Return only the answer, without the "Answer:" prefix
            except Exception as e:
                return f"⚠️ An error occurred while processing your request: {e}"


    def update_llm(self, llm_choice: str, **kwargs):
        self.llm_choice = llm_choice
        if llm_choice == "ollama":
            self.llm_model = kwargs.get("model", self.llm_model)
            self.llm_temperature = kwargs.get("temperature", self.llm_temperature)
        elif llm_choice == "openai":
            self.openai_model = kwargs.get("model", self.openai_model)
            self.openai_temperature = kwargs.get("temperature", self.openai_temperature)
            self.openai_api_key = kwargs.get("api_key", self.openai_api_key)
        
        self.initialize_llm()
        self.initialize_qa_chain()