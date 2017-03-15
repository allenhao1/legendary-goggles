import matplotlib.pyplot as plt, pandas as pd, numpy as np, matplotlib as mpl, requests, time
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
from scipy.spatial.distance import cdist, pdist, euclidean
from sklearn.cluster import KMeans
from sklearn import metrics
from pprint import pprint
from pymongo import MongoClient
import pymongo

client = MongoClient('mongodb://localhost:27017/')
db = client['2kdb']['try2']

players = []
positionConvert = {"PG" : 1, "SG" : 2, "SF" : 3, "PF" : 4, "C" : 5, "N/A" : -1}

playersDB = db.find()

for player in playersDB:
    player["Position"] = positionConvert[player["Position"]]
    player["Secondary position"] = positionConvert[player["Secondary position"]]
    if player['Name'][:3] == "Nen":
        player['Name'] = "Nene"
    if player['Overall'] > 40:
        players.append(player)
# print data


df = pd.DataFrame(players)

# Rearrange columns
cols = list(df)
cols.insert(0, cols.pop(cols.index('Overall')))
df = df.ix[:, cols]
cols.insert(0, cols.pop(cols.index('Height')))
df = df.ix[:, cols]
cols.insert(0, cols.pop(cols.index('Secondary position')))
df = df.ix[:, cols]
cols.insert(0, cols.pop(cols.index('Position')))
df = df.ix[:, cols]
cols.insert(0, cols.pop(cols.index('_id')))
df = df.ix[:, cols]
cols.insert(0, cols.pop(cols.index('Name')))
df = df.ix[:, cols]

overall = df['Overall']
secondary = df['Secondary position']
position = df['Position']
_id = df['_id']
name = df['Name']

df = df.drop(['_id', 'Secondary position', 'Position', '_id','Name'], 1)

# Code from http://www.danvatterott.com/blog/2016/02/21/grouping-nba-players/
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

X = df.as_matrix() #take data out of dataframe
X = scale(X) #standardize the data before giving it to the PCA.
#I standardize the data because some features such as PF or steals have lower magnitudes than other features such as FG2A
#I want both to contribute equally to the PCA, so I make sure they're on the same scale.

pca = PCA() #great PCA object
pca.fit(X) #pull out principle components


from sklearn.cluster import KMeans


reduced_data = PCA(n_components=5, whiten=True).fit_transform(X) #transform data into the 5 PCA components space
#kmeans assumes clusters have equal variance, and whitening helps keep this assumption.

final_fit = KMeans(n_clusters=7).fit(reduced_data) #fit 7 clusters

from scipy.spatial.distance import euclidean

def distance_to_centroid(row, vals, centroid):
    return euclidean(row, centroid)


df['distance_to_center0'] = df.apply(lambda r: distance_to_centroid(r,reduced_data,
    final_fit.cluster_centers_[0]),1)
df['distance_to_center1'] = df.apply(lambda r: distance_to_centroid(r,reduced_data,
    final_fit.cluster_centers_[1]),1)
df['distance_to_center2'] = df.apply(lambda r: distance_to_centroid(r,reduced_data,
    final_fit.cluster_centers_[2]),1)
df['distance_to_center3'] = df.apply(lambda r: distance_to_centroid(r,reduced_data,
    final_fit.cluster_centers_[3]),1)
df['distance_to_center4'] = df.apply(lambda r: distance_to_centroid(r,reduced_data,
    final_fit.cluster_centers_[4]),1)
df['distance_to_center5'] = df.apply(lambda r: distance_to_centroid(r,reduced_data,
    final_fit.cluster_centers_[5]),1)
df['distance_to_center6'] = df.apply(lambda r: distance_to_centroid(r,reduced_data,
    final_fit.cluster_centers_[6]),1)

df.head()


df['kmeans_label'] = final_fit.labels_ #label each data point with its clusters
df['PLAYER_ID'] = _id #of course we want to know what players are in what cluster
# because playerID #s mean nothing to me, lets get the names too
df['Name'] = name

#lets also create a dataframe with data about where the clusters occur in the 5 component PCA space.
# cluster_locs = pd.DataFrame(final_fit.cluster_centers_,columns=['component %s'% str(s) for s in range(np.size(final_fit.cluster_centers_,1))])

df.to_csv('cluster2.csv')
