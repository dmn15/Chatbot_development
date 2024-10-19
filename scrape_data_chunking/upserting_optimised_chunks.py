from langchain_text_splitters import RecursiveJsonSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import json
import uuid
import os

# Initialize encoder and Qdrant client
encoder = SentenceTransformer("BAAI/bge-m3")
qdrant_client = QdrantClient(host='localhost', port=6333, timeout=10)

# Path to output directories
output_base_dir = "."

# Collection name
collection_name = "Rishabh_Collection"

# Create the collection in Qdrant
qdrant_client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=encoder.get_sentence_embedding_dimension(),
        distance=models.Distance.COSINE,
        on_disk=True
    )
)

# Prepare a list to store points for batch upsert
points = []

# Iterate through all directories that match the pattern 'output_dictionary_*'
for dir_name in os.listdir(output_base_dir):
    if dir_name.startswith('output_dictionary_'):
        dir_path = os.path.join(output_base_dir, dir_name)
        
        # Iterate through each JSON file in the directory
        for file_name in os.listdir(dir_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(dir_path, file_name)
                
                # Load the content of the JSON file
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                    
                    # Assuming the content is wrapped in brackets, so we get the first item
                    content = json_data[0]  # Unwrapping if necessary
                    
                    # Generate a unique point ID
                    point_id = str(uuid.uuid4())
                    
                    # Create the point and encode the content for Qdrant
                    points.append(
                        models.PointStruct(
                            id=point_id,
                            vector=encoder.encode(str(content)).tolist(),  # Encode the content
                            payload=content  # Add the content as payload
                        )
                    )

# Upsert the collected points into Qdrant
if points:
    qdrant_client.upsert(collection_name=collection_name, points=points)

print(f"All chunks from JSON files in '{output_base_dir}' have been inserted into Qdrant!")
