import json
import os
from collections import Counter
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()


def extract_locations(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    locations = []
    for key, firm_data in data.items():
        if isinstance(firm_data, dict) and "location" in firm_data:
            locations.append(firm_data["location"])

    return locations


def create_locations_cache(input_dir, cache_file):
    locations_counter = Counter()

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            locations = extract_locations(file_path)
            locations_counter.update(locations)

    # Save locations and counts to cache file
    Path(os.path.dirname(cache_file)).mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w") as outfile:
        json.dump(dict(locations_counter), outfile, indent=4, ensure_ascii=False)


# Define the input directory and cache file path
input_directory = "data/processed/svindkal_structured"
cache_file_path = "data/locations/locations_cache.json"

# Ensure that cache directory exists
Path(os.path.dirname(cache_file_path)).mkdir(parents=True, exist_ok=True)

# Create the locations cache
create_locations_cache(input_directory, cache_file_path)

# Define the geocoding function and append ", Sweden" to the address
def geocode(address, api_key):
    address = address + ", Sweden"  # Append ", Sweden" to the address
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': api_key}
    response = requests.get(url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']
        print(f"Geocoded {address} as {lat}, {lng}")
        return lat, lng
    else:
        return None, None

# Google Maps Geocoding API key from .env called GOOGLE_MAPS_API_KEY with dotenv
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

# Load locations from JSON file
with open('data/locations/locations_cache.json', 'r') as file:
    locations = json.load(file)

# Dictionary to store geocoded coordinates
geocoded_locations = {}

# Geocode each location
for location in locations.keys():
    lat, lng = geocode(location, api_key)
    if lat is not None and lng is not None:
        geocoded_locations[location] = {'Latitude': lat, 'Longitude': lng}

# Save the geocoded locations to a new JSON file
with open('data/locations/geocoded_locations.json', 'w') as outfile:
    json.dump(geocoded_locations, outfile, indent=4, ensure_ascii=False)



# Define the function to update the files with coordinates

def update_files_with_coordinates(input_dir, output_dir, geocoded_locations_file):
    # Load geocoded locations
    with open(geocoded_locations_file, 'r') as file:
        geocoded_locations = json.load(file)

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_file_path = os.path.join(input_dir, filename)

            with open(input_file_path, 'r') as file:
                data = json.load(file)

            # Update each firm's data with coordinates
            for key, firm_data in data.items():
                if isinstance(firm_data, dict) and 'location' in firm_data:
                    location = firm_data['location']
                    coordinates = geocoded_locations.get(location, None)
                    firm_data['coordinates'] = coordinates

            # Save the updated data to the output directory
            output_file_path = os.path.join(output_dir, filename)
            with open(output_file_path, 'w') as outfile:
                json.dump(data, outfile, indent=4, ensure_ascii=False)

# Define the input and output directories and the geocoded locations file
input_directory = 'data/processed/svindkal_structured'
output_directory = 'data/processed/svindkal_geocoded'
geocoded_locations_file = 'data/locations/geocoded_locations.json'

# Create output directory if it doesn't exist
Path(output_directory).mkdir(parents=True, exist_ok=True)

# Update the files with coordinates
update_files_with_coordinates(input_directory, output_directory, geocoded_locations_file)
