import os
import json
import folium
import random
from folium.plugins import MarkerCluster

# Function to create a popup message with the desired keys, including the company name as an h3
def create_popup_with_name(info):
    details = [f"<h3>{info.get('name', 'N/A')}</h3>",
               f"<b>Location:</b> {info.get('location', 'N/A')}",
               f"<b>Foundation Year:</b> {info.get('foundation_year', 'N/A')}",
               f"<b>Business:</b> {info.get('business', 'N/A')}",
               f"<b>Products:</b> {info.get('products', 'N/A')}",
               f"<b>Financials:</b> {info.get('financials', 'N/A')}"]
    return '<br>'.join(details)

# Function to choose color based on the cluster
def choose_color(cluster):
    colors = ["red", "blue", "green", "purple", "orange", "darkred",
              "lightred", "beige", "darkblue", "darkgreen", "cadetblue",
              "darkpurple", "white", "pink", "lightblue", "lightgreen",
              "gray", "black", "lightgray"]
    return colors[cluster % len(colors)]

# Function to jitter coordinates slightly to avoid overlapping markers
def jitter_coordinates(lat, lon, magnitude=0.001):
    return lat + random.uniform(-magnitude, magnitude), lon + random.uniform(-magnitude, magnitude)

# Cluster mapping
cluster_mapping = {
    0: "Construction contractors",
    1: "Other firms",
    2: "Food and beverage manufacturers",
    3: "Textile and clothing manufacturers",
    4: "Missing data",
    5: "Paper and book manufacturers",
    6: "Mechanical workshops",
    7: "Wood products industries",
    8: "Furniture manufacturers",
    9: "Clothing manufacturers and retailers"
}

# Color mapping for each cluster
color_mapping = {
    0: "red",
    1: "blue",
    2: "green",
    3: "purple",
    4: "orange",
    5: "darkred",
    6: "lightred",
    7: "beige",
    8: "darkblue",
    9: "lightblue"
}

# Directory containing the JSON files
directory = 'data/processed/svindkal_numeric/'

# Create a Folium map
m = folium.Map(location=[59.3293, 18.0686], zoom_start=6)

# Create clusters with names from cluster_mapping
clusters = {i: MarkerCluster(name=cluster_mapping[i]).add_to(m) for i in range(10)}

# Iterate through each JSON file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".json"):
        file_path = os.path.join(directory, filename)

        # Load the JSON data
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Plot each company on the map
        for key, value in data.items():
            if "coordinates" in value and "cluster" in value:
                try:
                    lat = value["coordinates"]["Latitude"]
                    lon = value["coordinates"]["Longitude"]
                    cluster = value["cluster"]

                    # Jitter the coordinates to avoid overlapping markers
                    jittered_lat, jittered_lon = jitter_coordinates(lat, lon)

                    # Update popup content to use cluster name
                    cluster_name = cluster_mapping.get(cluster, "Unknown Cluster")
                    popup_content = f"{create_popup_with_name(value)}<br>Cluster: {cluster_name}"

                    # Choose color based on cluster
                    color = color_mapping.get(cluster, "gray")

                    # Add the company to the appropriate cluster with a colored popup
                    folium.Marker(
                        [jittered_lat, jittered_lon],
                        popup=popup_content,
                        icon=folium.Icon(color=color)
                    ).add_to(clusters[cluster])
                except Exception as e:
                    print(f"Error processing data in {filename} for {key}: {e}")

# Add LayerControl to toggle clusters
folium.LayerControl(collapsed=False).add_to(m)

# Save the map to an HTML file
output_file = 'data/maps/all_companies_map.html'
m.save(output_file)
print(f"Map saved to {output_file}")