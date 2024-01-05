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

def add_employees_total(data):
    for key in data.keys():
        company = data[key]
        if "financials" in company and isinstance(company["financials"], dict):
            employees_total = 0
            if "employees" in company["financials"] and isinstance(company["financials"]["employees"], dict):
                for emp_type, emp_count in company["financials"]["employees"].items():
                    if isinstance(emp_count, int):
                        employees_total += emp_count
            company["financials"]["employees_total"] = employees_total
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

        # Add total employees count
        data_with_employees = add_employees_total(converted_data)

        # Save the modified data to the output directory
        with open(os.path.join(output_dir, filename), 'w') as file:
            json.dump(data_with_employees, file, indent=4, ensure_ascii=False)

print("Conversion and employee count addition completed for all files.")
