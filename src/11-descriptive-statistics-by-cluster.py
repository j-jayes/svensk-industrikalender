import pandas as pd
import json
import os
import re

def extract_page_number(file_name):
    """ Extracts the page number from the file name. """
    match = re.search(r'_(\d+)\.json', file_name)
    return int(match.group(1)) if match else None

def flatten_json_to_df(file_path, file_index):
    """ Read and flatten JSON file into a DataFrame, selecting specific fields for each company. """
    with open(file_path, 'r') as file:
        data = json.load(file)

        all_rows = []  # To store all company rows

        for key, company in data.items():
            # Flatten the JSON data for each company
            df = pd.json_normalize(company, sep='_')

            # Define all possible fields
            possible_fields = [
                'name', 'location', 'business', 'products', 'financials_capital',
                'financials_annual_turnover', 'financials_employees_total', 
                'foundation_year', 'corporation_year', 'coordinates_Latitude', 
                'coordinates_Longitude', 'cluster'
            ]

            # Select only the fields that exist in this particular DataFrame
            selected_fields = [field for field in possible_fields if field in df.columns]

            # Filter the DataFrame to include only the selected fields
            row = df[selected_fields].iloc[0].to_dict()  # Convert the first row to a dictionary

            # Add file index and page number
            row['file_index'] = file_index
            row['page_number'] = extract_page_number(file_path)

            all_rows.append(row)

        return pd.DataFrame(all_rows)

# Directory where the JSON files are stored
directory_path = 'data/processed/svindkal_numeric' # Replace with your directory path

# Read and process all JSON files in the directory
all_dfs = []
for index, file_name in enumerate(os.listdir(directory_path)):
    if file_name.endswith('.json'):
        file_path = os.path.join(directory_path, file_name)
        df = flatten_json_to_df(file_path, index)
        all_dfs.append(df)

# Combine all data into a single DataFrame
combined_df = pd.concat(all_dfs, ignore_index=True)

combined_df.head()

# save the dataframe to an excel file
combined_df.to_excel('data/processed/svindkal_numeric/combined_df.xlsx', index=False)
