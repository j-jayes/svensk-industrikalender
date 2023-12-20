import os
import json
import re

def convert_currency_values(data):
    # Regex pattern to match numbers with commas followed by 'kr'
    pattern = re.compile(r'(\d{1,3}(?:,\d{3})+)\s*kr')

    # Function to recursively search and convert values in nested dictionary
    def search_and_convert(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    match = pattern.match(value)
                    if match:
                        # Convert string to a number by removing commas
                        obj[key] = int(match.group(1).replace(',', ''))
                else:
                    search_and_convert(value)
        elif isinstance(obj, list):
            for item in obj:
                search_and_convert(item)

    search_and_convert(data)
    return data
# Directory paths
input_dir = 'data/processed/svindkal_clustered/'
output_dir = 'data/processed/svindkal_numeric/'

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Loop through all files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.json'):
        with open(os.path.join(input_dir, filename), 'r') as file:
            data = json.load(file)

        # Convert currency values to numeric
        converted_data = convert_currency_values(data)

        # Save the modified data to the output directory
        with open(os.path.join(output_dir, filename), 'w') as file:
            json.dump(converted_data, file, indent=4, ensure_ascii=False)

print("Conversion completed for all files.")
