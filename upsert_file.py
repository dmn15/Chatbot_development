from langchain_text_splitters import RecursiveJsonSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import json
import uuid

encoder = SentenceTransformer("BAAI/bge-m3")
qdrant_client = QdrantClient(host='localhost', port=6333,timeout=10)


with open('/home/administrator/Documents/Rishabh_Bot/Rishabh_data/services_provided.json', 'r') as f:
    json_data = json.load(f)


collection_name = "Rishabh_Collection"

# qdrant_client.create_collection(
#     collection_name=collection_name,
#     vectors_config=models.VectorParams(
#             size=encoder.get_sentence_embedding_dimension(),
#             distance=models.Distance.COSINE, on_disk= True
#         ),
#     # hnsw_config=models.HnswConfigDiff(
#     #                     m=16,
#     #                     ef_construct=100,
#     #                     full_scan_threshold=2000
#     #                 )
# )


points=[]
for chunk in json_data:
        point_id = str(uuid.uuid4())
        points.append(
            models.PointStruct(
                id=point_id,
                vector=encoder.encode(str(chunk)).tolist(),  # Assuming encoder is defined and encode method works
                payload=chunk
            )
        )
    
qdrant_client.upsert(collection_name="Rishabh_Collection", points=points)

print("All chunks inserted into Qdrant!")

#------------------------------------------------------------


# The below is is to upsert multiple files from a folder called technology_usage_parts

# from langchain_text_splitters import RecursiveJsonSplitter
# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# from qdrant_client.http import models
# import json
# import uuid
# import os

# # Initialize encoder and Qdrant client
# encoder = SentenceTransformer("BAAI/bge-m3")
# qdrant_client = QdrantClient(host='localhost', port=6333, timeout=10)

# # Set the collection name
# collection_name = "Rishabh_Collection"

# # Create the collection (uncomment if needed)
# # qdrant_client.create_collection(
# #     collection_name=collection_name,
# #     vectors_config=models.VectorParams(
# #         size=encoder.get_sentence_embedding_dimension(),
# #         distance=models.Distance.COSINE,
# #         on_disk=True
# #     ),
# # )

# # Directory containing the JSON files
# directory = 'technology_usage_parts'

# # Process each file in the directory
# for filename in os.listdir(directory):
#     if filename.endswith('.json'):
#         file_path = os.path.join(directory, filename)
        
#         # Read the JSON file
#         with open(file_path, 'r') as f:
#             json_data = json.load(f)
        
#         points = []
#         for chunk in json_data:
#             point_id = str(uuid.uuid4())
#             points.append(
#                 models.PointStruct(
#                     id=point_id,
#                     vector=encoder.encode(str(chunk)).tolist(),
#                     payload=chunk
#                 )
#             )
        
#         # Upsert points for this file
#         qdrant_client.upsert(collection_name=collection_name, points=points)
#         print(f"Inserted chunks from {filename} into Qdrant!")

# print("All files processed and inserted into Qdrant!")