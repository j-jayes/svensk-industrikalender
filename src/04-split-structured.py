import json
import os
from pathlib import Path

def restructure_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    restructured_data = {}
    index = 1
    name_key_missing = False

    if 'structured' in data and isinstance(data['structured'], dict):
        for key, value in data['structured'].items():
            if isinstance(value, dict):
                if 'name' not in value:
                    name_key_missing = True
                restructured_data[str(index)] = value
                index += 1
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        if 'name' not in item:
                            name_key_missing = True
                        restructured_data[str(index)] = item
                        index += 1
                    else:
                        # Handle non-dictionary items in the list
                        name_key_missing = True
                        restructured_data[str(index)] = {"unknown_structure": item}
                        index += 1
            else:
                # Handle non-dictionary and non-list items
                name_key_missing = True
                restructured_data[str(index)] = {"unknown_structure": value}
                index += 1
    else:
        # Handle cases where 'structured' is not a dictionary
        name_key_missing = True
        restructured_data["1"] = {"unknown_structure": data}

    return restructured_data, name_key_missing

def process_files(input_dir, output_dir, check_dir):
    # Create output and check directories if they don't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(check_dir).mkdir(parents=True, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(input_dir, filename)
            restructured_data, name_key_missing = restructure_data(file_path)

            if name_key_missing:
                output_file_path = os.path.join(check_dir, filename)
            else:
                output_file_path = os.path.join(output_dir, filename)

            with open(output_file_path, 'w') as outfile:
                json.dump(restructured_data, outfile, indent=4, ensure_ascii=False)

# Define the input and output directories
input_directory = 'data/processed/svindkal'
output_directory = 'data/processed/svindkal_structured'
check_directory = 'data/processed/svindkal_check'

# Process the files
process_files(input_directory, output_directory, check_directory)
