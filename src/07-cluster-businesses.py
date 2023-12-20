from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import KMeans
import json
import umap
import pandas as pd
import plotly.express as px
import os

# Load the JSON data from the provided file
file_path = 'data/clustering/businesses.json'  # Update with the path to your JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# extract the business and products values from the dictionary
businesses = []
products = []
names = []

for file_name, file_data in data.items():
    for key, value in file_data.items():
        businesses.append(value['business'])
        products.append(value['products'])
        names.append(value['name'])

# Concatenate the business and products values
concatenated_texts = [f"{business} {products}" for business, products in zip(businesses, products)]

# take the first 5 items of the list
# concatenated_texts = concatenated_texts[:5]

# Load the sentence transformer model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# model_name = 'all-MiniLM-L6-v2'

model = SentenceTransformer('KBLab/sentence-bert-swedish-cased')

model_name = 'KBLab_sentence-bert-swedish-cased'

# Check if embeddings already exist in the cache file
cache_file_path = f'data/clustering/embeddings_{model_name}.json'


if os.path.exists(cache_file_path):
    # Read embeddings from the cache file
    with open(cache_file_path, 'r', encoding='utf-8') as file:
        embeddings = json.load(file)
else:
    # Generate embeddings for the concatenated texts
    embeddings = model.encode(concatenated_texts, convert_to_tensor=True)
    # Save embeddings to the cache file
    os.makedirs('data/clustering', exist_ok=True)
    with open(cache_file_path, 'w', encoding='utf-8') as file:
        json.dump(embeddings.tolist(), file, ensure_ascii=False, indent=4)


# Perform KMeans clustering
n_clusters = 10  # Example: setting 10 clusters, this can be adjusted based on the data
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(embeddings)

# Combining the results
clustered_data = [{'text': text, 'cluster': int(cluster)} for text, cluster in zip(concatenated_texts, cluster_labels)]

# Add the cluster number back to the original data called data
for file_name, file_data in data.items():
    for key, value in file_data.items():
        value['cluster'] = clustered_data.pop(0)['cluster']


# Save the data to a JSON file
os.makedirs('data/clustering', exist_ok=True)
with open('data/clustering/businesses_clustered.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)


# Dimensionality reduction with UMAP
# set seed for reproducibility
np.random.seed(42)
umap_reducer = umap.UMAP()
umap_embeddings = umap_reducer.fit_transform(embeddings)

# Prepare data for plotting
plot_data = {
    'x': umap_embeddings[:, 0],
    'y': umap_embeddings[:, 1],
    'cluster': cluster_labels,
    'name': names,
    'text': concatenated_texts
}

# Create a scatter plot
fig = px.scatter(plot_data, x='x', y='y', color='cluster', hover_data=['name', 'text'])
fig.update_layout(title='Cluster Visualization of Firms', xaxis_title='UMAP 1', yaxis_title='UMAP 2')
fig.show()







# count the most common n terms in clustered_data for each cluster
n = 10

# create a dataframe from clustered_data
df = pd.DataFrame(clustered_data)

# create a dataframe with the most common n terms for each cluster
df_top_n = pd.DataFrame(columns=['cluster', 'term', 'count'])

for cluster in range(n_clusters):
    # filter the dataframe to only include the current cluster
    df_cluster = df[df['cluster'] == cluster]
    # count the most common n terms in the cluster
    df_cluster_top_n = pd.DataFrame(df_cluster['text'].str.split(expand=True).stack().value_counts().head(n))
    # reset the index
    df_cluster_top_n.reset_index(inplace=True)
    # rename the columns
    df_cluster_top_n.columns = ['term', 'count']
    # add the cluster column
    df_cluster_top_n['cluster'] = cluster
    # concat the cluster dataframe to the top n dataframe
    df_top_n = pd.concat([df_top_n, df_cluster_top_n])

# to csv in data/clustering
os.makedirs('data/clustering', exist_ok=True)
df_top_n.to_csv('data/clustering/top_n_terms.csv', index=False)

# create a bar chart
fig = px.bar(df_top_n, x='term', y='count', color='cluster', hover_data=['cluster'])
fig.update_layout(title=f'Top {n} terms per cluster')
fig.show()

