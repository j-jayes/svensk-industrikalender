
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import pandas as pd

data = pd.read_excel('data/processed/svindkal_numeric/combined_df.xlsx')


# Prepare data
coordinates = data[['coordinates_Latitude', 'coordinates_Longitude']].dropna()
coordinates_scaled = StandardScaler().fit_transform(coordinates)

# Run DBSCAN
dbscan = DBSCAN(eps=0.15, min_samples=30)  # Adjust eps and min_samples
clusters = dbscan.fit_predict(coordinates_scaled)

# Add cluster labels to your dataframe
data['dbscan_cluster'] = np.nan
data.loc[coordinates.index, 'dbscan_cluster'] = clusters

# Now you can proceed to calculate firm specificity within these clusters

# make a map with the dots coloured by dbscan_cluster
import plotly.express as px
fig = px.scatter(data, x='coordinates_Longitude', y='coordinates_Latitude', color='dbscan_cluster')
fig.show()

# save the file to "data/output/dbscan_clusters.xlsx"
data.to_excel('data/output/dbscan_clusters.xlsx', index=False)

from scipy.stats import chi2_contingency
import numpy as np

# Extracting the relevant columns for the analysis
business_type = data['cluster']
geo_cluster = data['dbscan_cluster']

# Creating a contingency table
contingency_table = pd.crosstab(business_type, geo_cluster)

# Calculating log odds
def calculate_log_odds(contingency_table):
    odds_ratios = np.zeros(contingency_table.shape)

    for i in range(contingency_table.shape[0]):
        for j in range(contingency_table.shape[1]):
            # Calculate the odds of a business type in a specific geographic region
            odds = contingency_table.iloc[i, j] / (contingency_table.sum(axis=1)[i] - contingency_table.iloc[i, j])

            # Calculate the odds of a business type in all other geographic regions
            other_odds = (contingency_table.iloc[i, :].sum() - contingency_table.iloc[i, j]) / \
                         (contingency_table.sum().sum() - contingency_table.iloc[i, :].sum())

            # Calculate log odds ratio
            odds_ratios[i, j] = np.log(odds / other_odds)

    return pd.DataFrame(odds_ratios, index=contingency_table.index, columns=contingency_table.columns)

log_odds_table = calculate_log_odds(contingency_table)

# Finding the highest log odds for each geographic cluster to determine the most specific business type to it
most_specific_business = log_odds_table.idxmax(axis=0)

most_specific_business

# Create a dictionary for the most common business using the contingency_table and counting the most freqeunt business type for each dbscan cluster
most_common_business = contingency_table.idxmax(axis=0)

# join the most common business and most specific business back to the original dataframe on dbscan
most_common_business = pd.DataFrame(most_common_business, columns=['most_common_business'])
most_specific_business = pd.DataFrame(most_specific_business, columns=['most_specific_business'])
most_common_business = most_common_business.join(most_specific_business)
data = data.join(most_common_business, on='dbscan_cluster')

# save the file to "data/output/dbscan_clusters_business_counts.xlsx"
data.to_excel('data/output/dbscan_clusters_business_counts.xlsx', index=False)