from langchain_ollama import ChatOllama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import json

# Initialize Qdrant client
qdrant_client = QdrantClient(host='localhost', port=6333, timeout=10)

# Initialize the encoder
encoder = SentenceTransformer("BAAI/bge-m3")

def initialize_llm(llm_model="llama3.2:3b", llm_temperature=0):
    return ChatOllama(
        model=llm_model,
        temperature=llm_temperature,
    )

def initialize_chain(llm):
    prompt_template = """Use the following pieces of information to answer the user's question fron the given Context only.
    Please go through the context thoroughly and answer the question. Give a detailed Answer.
    If you don't get the answer from the context given below, just say that you don't know, don't try to make up an answer.

    Context:
    {context}

    Question: {question}

    Only return the helpful answer.
    Helpful answer:
    """
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=['context', 'question']
    )
    return LLMChain(llm=llm, prompt=prompt)

def get_similar_chunks(query: str, top_k: int = 5):
    query_vector = encoder.encode(query).tolist()
    search_result = qdrant_client.search(
        collection_name="Rishabh_Collection_test",
        query_vector=query_vector,
        limit=top_k
    )
    return [json.dumps(hit.payload, indent=2) for hit in search_result]

def get_response(chain, query: str) -> str:
    try:
        # Get similar chunks
        similar_chunks = get_similar_chunks(query)
        
        # Combine chunks into a single context string
        context = "\n\n".join(similar_chunks)
        
        # Get response from the language model
        response = chain.run(context=context, question=query)
        print("Context:", context)
        return response
    except Exception as e:
        return f"⚠️ An error occurred while processing your request: {e}"

# Initialize the LLM and chain
llm = initialize_llm(llm_model="llama3.2:3b", llm_temperature=0)
chain = initialize_chain(llm)

# Example usage
query = "whata re the challenges of Real-time Bank Fraud Detection and Prevention Software?"

response = get_response(chain, query)
print("Query:", query)
print("\nResponse:", response)