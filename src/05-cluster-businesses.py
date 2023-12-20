import json
import os

# Define the path where the JSON files are located
json_files_path = 'data/processed/svindkal_geocoded'

def extract_data_from_json_with_error_handling(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        extracted_data = {}
        for key, value in data.items():
            # Extracting name, business, and products with error handling
            extracted_data[key] = {
                'name': value.get('name', None),
                'business': value.get('business', None),
                'products': value.get('products', None)
            }
        return extracted_data
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
    except KeyError:
        print(f"Unexpected data structure in file: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred while processing file {file_path}: {e}")

# Process all JSON files in the specified directory with the revised function
extracted_data_all_files_with_error_handling = {}
for file_name in os.listdir(json_files_path):
    if file_name.endswith('.json'):
        file_path = os.path.join(json_files_path, file_name)
        extracted_data = extract_data_from_json_with_error_handling(file_path)
        if extracted_data:
            extracted_data_all_files_with_error_handling[file_name] = extracted_data

# Show a summary of the extracted data with error handling
extracted_data_summary_with_error_handling = {k: list(v.values())[:2] for k, v in extracted_data_all_files_with_error_handling.items()}  # Show first two entries for each file

# Save the extracted data to a JSON file called "data/clustering/businesses.json"
# ensure path exists
os.makedirs('data/clustering', exist_ok=True)

with open('data/clustering/businesses.json', 'w', encoding='utf-8') as file:
    json.dump(extracted_data_all_files_with_error_handling, file, ensure_ascii=False, indent=4)



