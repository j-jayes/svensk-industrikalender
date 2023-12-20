import json
import os

# File paths
main_file_path = 'data/clustering/businesses_clustered.json'
source_directory = "data/processed/svindkal_geocoded/"
destination_directory = 'data/processed/svindkal_clustered/'

# Ensure the destination directory exists
if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)

# Read the main file to get the cluster numbers
with open(main_file_path, 'r') as file:
    clusters_data = json.load(file)

# Process each file referenced in the main file
for file_name, businesses in clusters_data.items():
    source_file_path = os.path.join(source_directory, file_name)
    destination_file_path = os.path.join(destination_directory, file_name)

    # Read the content of the source file
    if os.path.exists(source_file_path):
        with open(source_file_path, 'r') as file:
            data = json.load(file)

        # Update each business entry with the cluster number
        for key, business in businesses.items():
            if key in data:
                data[key]['cluster'] = business['cluster']

        # Write the updated data to the destination file
        with open(destination_file_path, 'w') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    else:
        print(f"File not found: {source_file_path}")

print("Data processing complete.")
