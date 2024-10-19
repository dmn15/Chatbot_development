# Below code is to make the industries.json file from case_studies.json file

# import json

# # Load the JSON data from the file
# with open('/home/administrator/Documents/Rishabh_Bot/Rishabh_data/case_studies.json', 'r') as file:
#     data = json.load(file)

# # Extract the value of "Industry" from each element in the list
# industries = []
# for case_study in data:
#     other_details = case_study.get("other_details", {})
#     industry = other_details.get("Industry")
#     if industry and industry not in industries:
#         industries.append(industry)

# # Create the final JSON structure
# industries_data = {
#     "Industries company worked in": industries
# }

# # Save the structured data to a JSON file
# with open('industries.json', 'w') as file:
#     json.dump(industries_data, file, indent=4)

# print("Industries data saved to industries.json")




#------------------------------------------------------------

# This is the code to make technology_usage.json, just 1 file containing all the technologies and their case studies

# import json

# # Load the JSON data from the file
# with open('/home/administrator/Documents/Rishabh_Bot/Rishabh_data/case_studies.json', 'r') as file:
#     data = json.load(file)

# # Create a dictionary to store the mapping of technologies to case studies
# technology_mapping = {}

# # Extract the technology_used values from each case study
# for case_study in data:
#     case_study_title = case_study.get("title", "Unnamed Case Study")
#     technologies = case_study.get("technology_used", [])
#     for tech in technologies:
#         if tech not in technology_mapping:
#             technology_mapping[tech] = []
#         technology_mapping[tech].append(case_study_title)

# # Create the final JSON structure
# technology_data = {
#     "Technology Usage in Case Studies": technology_mapping
# }

# # Save the structured data to a JSON file
# with open('technology_usage.json', 'w') as file:
#     json.dump(technology_data, file, indent=4)

# print("Technology usage data saved to technology_usage.json")

#------------------------------------------------------------

#below is the code to make technology_usage_parts directory in which there are multiple json files for each technology

# import json
# import os

# # Load the JSON data from the file
# with open('/home/administrator/Documents/Rishabh_Bot/technology_usage.json', 'r') as file:
#     data = json.load(file)

# # Create a directory to save the structured JSON files
# output_dir = 'technology_usage_parts'
# os.makedirs(output_dir, exist_ok=True)

# # Extract the technology usage data
# technology_usage = data.get("Technology Usage in Case Studies", {})

# # Function to save data to a JSON file
# def save_to_json(data, filename):
#     with open(os.path.join(output_dir, filename), 'w') as file:
#         json.dump([data], file, indent=4)  # Wrap the data in a list

# # Breakdown the data into smaller parts
# for technology, case_studies in technology_usage.items():
#     structured_data = {
#         "technology": technology,
#         "case_studies": case_studies
#     }
#     filename = f"{technology.replace(' ', '_').replace('/', '_')}.json"
#     save_to_json(structured_data, filename)

# print(f"Structured data saved to {output_dir} directory.")


#----------------------------------------------------------------------

# Below code is to make services_provided.json

import json

# Load the JSON data from the file
with open('/home/administrator/Documents/Rishabh_Bot/Rishabh_data/scraped_data.json', 'r') as file:
    data = json.load(file)

# Create a list to store the extracted information
extracted_data = []

# Extract the specific part of the URL
for item in data:
    url = item.get("url", "")
    if url:
        # Extract the part after the last '/'
        url_part = url.rstrip('/').split('/')[-1]
        extracted_data.append(url_part)

# Create the final JSON structure
services_data = {
    "services provided by the company": extracted_data
}

# Save the extracted information to a new JSON file
output_file = 'services_provided.json'
with open(output_file, 'w') as file:
    json.dump(services_data, file, indent=4)

print(f"Extracted data saved to {output_file}")