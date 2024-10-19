import json
import os
from collections import Counter
from urllib.parse import urlparse

def get_unique_identifier(dictionary):
    """Generate a unique identifier for the dictionary."""
    if 'url' in dictionary:
        # Extract the last part of the URL path
        path = urlparse(dictionary['url']).path
        return path.split('/')[-1] or path.split('/')[-2]  # Use second-to-last if last is empty
    
    # Fallback to other keys if 'url' is not present
    for key in ['source', 'id']:
        if key in dictionary:
            return str(dictionary[key])
    
    # If no preferred keys are found, use the first key-value pair
    if dictionary:
        first_key = next(iter(dictionary))
        return f"{first_key}:{dictionary[first_key]}"
    return "unknown"

def split_dictionary(dictionary):
    identifier = get_unique_identifier(dictionary)
    
    sections = []

    # Process each top-level key in the dictionary
    for key, value in dictionary.items():
        if key in ['service_we_offer', 'service_banner']:
            # Keep these sections intact
            sections.append({
                "identifier": identifier,
                "type": key,
                "content": value
            })
        elif key == 'service_page_tabs':
            # Handle service_page_tabs separately
            if isinstance(value, dict):
                # Add main paragraph as a separate section
                if 'main_paragraph' in value:
                    sections.append({
                        "identifier": identifier,
                        "type": "service_page_tabs_main_paragraph",
                        "content": value['main_paragraph']
                    })
                # Break down services
                if 'services' in value and isinstance(value['services'], list):
                    for i, service in enumerate(value['services']):
                        sections.append({
                            "identifier": identifier,
                            "type": "service_page_tabs_service",
                            "index": i,
                            "content": service
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
        elif isinstance(value, dict):
            # If the value is a dictionary, create a section for each key-value pair
            for sub_key, sub_value in value.items():
                sections.append({
                    "identifier": identifier,
                    "type": f"{key}_{sub_key}",
                    "content": sub_value
                })
        # Note: base.json file creation is removed here.
    
    return sections

def save_to_files(sections, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # Use a counter to handle potential duplicate type names
    type_counter = Counter()
    
    for section in sections:
        section_type = section['type']
        type_counter[section_type] += 1
        count = type_counter[section_type]
        
        filename = f"{section_type}_{count}.json"
        # Wrap the section content in square brackets as per the request
        section_with_brackets = [section]
        
        with open(os.path.join(output_dir, filename), "w") as f:
            json.dump(section_with_brackets, f, indent=2)

def save_identifiers_list(identifiers, output_dir):
    """Save the list of unique identifiers to a file."""
    with open(os.path.join(output_dir, "unique_identifiers.json"), "w") as f:
        json.dump(identifiers, f, indent=2)

# Example usage
with open("/home/administrator/Documents/Web_Scraping/data/scraped_data.json", "r") as f:
    data = json.load(f)

identifiers = []

for i, dictionary in enumerate(data):
    sections = split_dictionary(dictionary)
    save_to_files(sections, f"output_dictionary_{i}")
    identifiers.append(sections[0]["identifier"])

# Save the list of unique identifiers
save_identifiers_list(identifiers, ".")

print(f"Processed {len(data)} dictionaries.")
print(f"List of unique identifiers saved to unique_identifiers.json")
