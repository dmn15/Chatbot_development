import os
import json
from typing import List
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    CSVLoader,
    UnstructuredExcelLoader
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    PythonCodeTextSplitter
)
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

class EmbeddingsManager:
    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: str = "cpu",
        encode_kwargs: dict = {"normalize_embeddings": True},
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "Rishabh_Collection",
    ):
        self.model_name = model_name
        self.device = device
        self.encode_kwargs = encode_kwargs
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name

        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": self.device},
            encode_kwargs=self.encode_kwargs,
        )

        self.client = QdrantClient(url=self.qdrant_url,timeout=10)

        # Get the embedding dimension
        self.embedding_dimension = len(self.embeddings.embed_query("test"))

    def load_document(self, file_path: str):
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        if file_extension == '.pdf':
            return UnstructuredPDFLoader(file_path).load()
        elif file_extension == '.md':
            return UnstructuredMarkdownLoader(file_path).load()
        elif file_extension in ['.ppt', '.pptx']:
            return UnstructuredPowerPointLoader(file_path).load()
        elif file_extension == '.csv':
            return CSVLoader(file_path).load()
        elif file_extension in ['.xls', '.xlsx']:
            return UnstructuredExcelLoader(file_path).load()
        elif file_extension == '.json':
            return self.load_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def load_json(self, file_path: str) -> List[Document]:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        
        documents = []
        for item in json_data:
            # Convert each dictionary to a formatted string
            content = json.dumps(item, indent=2)
            # Create a Document object for each item
            doc = Document(page_content=content, metadata={"source": file_path})
            documents.append(doc)
        
        return documents

    def split_documents(self, docs: List[Document], file_extension: str) -> List[Document]:
        if file_extension == '.json':
            return docs
        elif file_extension == '.md':
            splitter = MarkdownTextSplitter(chunk_size=1500, chunk_overlap=300)
        elif file_extension in ['.py', '.ipynb']:
            splitter = PythonCodeTextSplitter(chunk_size=1000, chunk_overlap=200)
        else:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        return splitter.split_documents(docs)

    def create_embeddings(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Load and preprocess the document
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        if file_extension == '.json':
            docs = self.load_json(file_path)
        else:
            docs = self.load_document(file_path)

        if not docs:
            raise ValueError("No documents were loaded from the file.")

        splits = self.split_documents(docs, file_extension)
        if not splits:
            raise ValueError("No text chunks were created from the documents.")

        # Create and store embeddings in Qdrant with HNSW index
        try:
            # Check if collection exists, if not create it with HNSW index
            collections = self.client.get_collections().collections
            if not any(collection.name == self.collection_name for collection in collections):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(
                        size=self.embedding_dimension,
                        distance=rest.Distance.COSINE
                    ),
                    # hnsw_config=rest.HnswConfigDiff(
                    #     m=16,
                    #     ef_construct=100,
                    #     full_scan_threshold=10000
                    # )
                )

            # Create Qdrant instance with HNSW index
            qdrant = Qdrant(
                client=self.client,
                collection_name=self.collection_name,
                embeddings=self.embeddings,
            )

            # Add documents to the collection
            qdrant.add_documents(splits)

        except Exception as e:
            raise ConnectionError(f"Failed to connect to Qdrant or create embeddings: {e}")

        return "✅ Vector DB Successfully Created and Stored in Qdrant with HNSW index!"