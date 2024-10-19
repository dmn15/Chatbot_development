import streamlit as st
from langchain_ollama import ChatOllama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
import json

# Initialize Qdrant client
qdrant_client = QdrantClient(host='localhost', port=6333, timeout=10)

# Initialize the encoder
encoder = SentenceTransformer("BAAI/bge-m3")

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

def initialize_llm(llm_model="llama3.2:3b", llm_temperature=0.5):
    return ChatOllama(
        model=llm_model,
        temperature=llm_temperature,
        streaming=True
    )

def initialize_chain(llm):
    prompt_template = """
You are a chatbot for the Rishabh Software website. Your task is to provide helpful answers based solely on the given Context and Question. Please follow these guidelines:

Carefully read and analyze the provided Context.
Answer the Question using only the information found in the Context.
Provide a detailed and helpful answer, using bullet points where appropriate.
Do not invent or include any information that is not present in the Context.
If the answer cannot be found in the Context, respond with "I'm sorry, but I don't have enough information to answer that question based on the provided context."

Context: {context}
Question: {question}
Please provide your helpful answer below:
"""
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=['context', 'question']
    )
    return LLMChain(llm=llm, prompt=prompt)

def get_similar_chunks(query: str, top_k: int = 5):
    query_vector = encoder.encode(query).tolist()
    search_result = qdrant_client.search(
        collection_name="Rishabh_Collection",
        query_vector=query_vector,
        limit=top_k
    )
    return [json.dumps(hit.payload, indent=2) for hit in search_result]

# Streamlit app
st.title("Rishabh Website Chatbot with llama3.2:3b")

# Initialize the LLM and chain
@st.cache_resource
def load_llm_chain():
    llm = initialize_llm(llm_model="llama3.2:3b", llm_temperature=0)
    return initialize_chain(llm)

chain = load_llm_chain()

# User input
user_question = st.text_input("Enter your question:")

if user_question:
    # Create a placeholder for the streaming response
    response_placeholder = st.empty()
    stream_handler = StreamHandler(response_placeholder)
    
    similar_chunks = get_similar_chunks(user_question)
    context = "\n\n".join(similar_chunks)
    
    # Generate the response with streaming
    chain({"context": context, "question": user_question}, callbacks=[stream_handler])

    if st.checkbox("Show Context"):
        st.text_area("Context:", value=context, height=300)