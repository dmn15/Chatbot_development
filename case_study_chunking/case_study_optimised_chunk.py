import json
import os
import uuid
from collections import Counter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialize the encoder and Qdrant client
encoder = SentenceTransformer("BAAI/bge-m3")
qdrant_client = QdrantClient(host='localhost', port=6333, timeout=10)

# Function to break down each dictionary based on its keys
def break_down_dictionary(dictionary):
    identifier = dictionary.get("title", str(uuid.uuid4()))  # Use 'title' as the identifier or a UUID if missing
    sections = []
    
    for key, value in dictionary.items():
        # Log the key being processed
        print(f"Processing key: {key} in dictionary with identifier: {identifier}")

        # If the key is 'key_features', 'solutions', or 'technology_used', keep it intact
        if key in ['key_features', 'solutions', 'technology_used']:
            sections.append({
                "identifier": identifier,
                "type": key,
                "content": value
            })
            print(f"Kept section intact for key: {key} in identifier: {identifier}")
        elif isinstance(value, dict):
            # If the value is a dictionary, break it down further
            for sub_key, sub_value in value.items():
                sections.append({
                    "identifier": identifier,
                    "type": f"{key}_{sub_key}",
                    "content": sub_value
                })
        elif isinstance(value, list):
            # If the value is a list, create a section for each item
            for i, item in enumerate(value):
                sections.append({
                    "identifier": identifier,
                    "type": f"{key}_item",
                    "index": i,
                    "content": item
                })
        else:
            # For simple values, treat them as individual sections
            sections.append({
                "identifier": identifier,
                "type": key,
                "content": value
            })
    
    return sections

# Function to save each section as a separate JSON file
def save_sections(sections, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # Ensure the base output directory exists
    type_counter = Counter()
    
    for section in sections:
        section_type = section['type']
        type_counter[section_type] += 1
        count = type_counter[section_type]
        
        filename = f"{section_type}_{count}.json"
        section_with_brackets = [section]  # Wrap the section content in square brackets
        
        # Ensure the subdirectory exists
        filepath = os.path.join(output_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Ensure subdirectory exists
        
        with open(filepath, "w") as f:
            json.dump(section_with_brackets, f, indent=2)

# Function to upsert the JSON files into the Qdrant database
def upsert_sections_to_qdrant(sections, collection_name):
    points = []
    
    for section in sections:
        point_id = str(uuid.uuid4())
        # Encode the content and prepare the point for upserting
        points.append(
            models.PointStruct(
                id=point_id,
                vector=encoder.encode(str(section)).tolist(),
                payload=section
            )
        )
    
    # Upsert points to the collection
    if points:
        qdrant_client.upsert(collection_name=collection_name, points=points)

# Create Qdrant collection
# collection_name = "Rishabh_Collection"
# qdrant_client.create_collection(
#     collection_name=collection_name,
#     vectors_config=models.VectorParams(
#         size=encoder.get_sentence_embedding_dimension(),
#         distance=models.Distance.COSINE,
#         on_disk=True
#     )
# )

# Load the JSON data (assuming multiple dictionaries in a list)
with open('/home/administrator/Documents/Web_Scraping/data/case_studies.json', 'r') as f:
    json_data = json.load(f)

# Iterate through the list of dictionaries, process each one, and store results
for idx, dictionary in enumerate(json_data):
    print(f"Processing dictionary {idx+1}/{len(json_data)} with title: {dictionary.get('title', 'No Title')}")
    sections = break_down_dictionary(dictionary)
    output_dir = f"output_dictionary_{idx}"
    
    # Save the sections to files
    save_sections(sections, output_dir)
    
    # Upsert the sections into Qdrant
    upsert_sections_to_qdrant(sections, 'Rishabh_Collection')

print("All dictionaries have been processed and upserted into Qdrant!")
