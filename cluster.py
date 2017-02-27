import matplotlib.pyplot as plt, pandas as pd, numpy as np, matplotlib as mpl, requests, time
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
from scipy.spatial.distance import cdist, pdist, euclidean
from sklearn.cluster import KMeans
from sklearn import metrics
from pprint import pprint
from db import db

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

df = df.drop(['_id', 'Secondary position', 'Position', '_id','Name', 'Overall durability', 'Potential', 'Intangibles'], 1)

# Code from http://www.danvatterott.com/blog/2016/02/21/grouping-nba-players/
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

X = df.as_matrix() #take data out of dataframe
X = scale(X) #standardize the data before giving it to the PCA.
#I standardize the data because some features such as PF or steals have lower magnitudes than other features such as FG2A
#I want both to contribute equally to the PCA, so I make sure they're on the same scale.

pca = PCA() #great PCA object
pca.fit(X) #pull out principle components
var_expl = pca.explained_variance_ratio_ #find amount of variance explained by each component
tot_var_expl = np.array([sum(var_expl[0:i+1]) for i,x in enumerate(var_expl)]) #create vector with cumulative variance

# plt.figure(figsize=(12,4)) #create cumulative proportion of variance plot
# plt.subplot(1,2,1)
# plt.plot(range(1,len(tot_var_expl)+1), tot_var_expl*100,'o-')
# plt.axis([0, len(tot_var_expl)+1, 0, 100])
# plt.xlabel('Number of PCA Components Included')
# plt.ylabel('Percentage of variance explained (%)')
#
# plt.subplot(1,2,2) #create scree plot
# plt.plot(range(1,len(var_expl)+1), var_expl*100,'o-')
# plt.axis([0, len(var_expl)+1, 0, 100])
# plt.xlabel('PCA Component');

loadings_df = pd.DataFrame(pca.components_, columns=df.columns)
from scipy.spatial.distance import cdist, pdist, euclidean
from sklearn.cluster import KMeans
from sklearn import metrics


#http://stackoverflow.com/questions/6645895/calculating-the-percentage-of-variance-measure-for-k-means
#The above link was helpful when writing this code.

reduced_data = PCA(n_components=5, whiten=True).fit_transform(X) #transform data into the 5 PCA components space
#kmeans assumes clusters have equal variance, and whitening helps keep this assumption.

k_range = range(2,31) #looking amount of variance explained by 1 through 30 cluster
k_means_var = [KMeans(n_clusters=k).fit(reduced_data) for k in k_range] #fit kmeans with 1 cluster to 30 clusters

#get labels and calculate silhouette score
labels = [i.labels_ for i in k_means_var]
sil_score = [metrics.silhouette_score(reduced_data,i,metric='euclidean') for i in labels]

centroids = [i.cluster_centers_ for i in k_means_var] #get the center of each cluster
k_euclid = [cdist(reduced_data,cent,'euclidean') for cent in centroids] #calculate distance between each item and each cluster center
dist = [np.min(ke,axis=1) for ke in k_euclid] #get the distance between each item and its cluster

wcss = [sum(d**2) for d in dist] #within cluster sum of squares
tss = sum(pdist(reduced_data)**2/reduced_data.shape[0]) #total sum of squares
bss = tss-wcss #between cluster sum of squares

plt.clf()
plt.figure(figsize=(12,4)) #create cumulative proportion of variance plot
plt.subplot(1,2,1)
plt.plot(k_range, bss/tss*100,'o-')
plt.axis([0, np.max(k_range), 0, 100])
plt.xlabel('Number of Clusters')
plt.ylabel('Percentage of variance explained (%)');

plt.subplot(1,2,2) #create scree plot
plt.plot(k_range, np.transpose(sil_score)*100,'o-')
plt.axis([0, np.max(k_range), 0, 40])
plt.xlabel('Number of Clusters');
plt.ylabel('Average Silhouette Score*100');

final_fit = KMeans(n_clusters=5).fit(reduced_data) #fit 6 clusters
df['kmeans_label'] = final_fit.labels_ #label each data point with its clusters
df['PLAYER_ID'] = _id #of course we want to know what players are in what cluster
# because playerID #s mean nothing to me, lets get the names too
df['Name'] = name

#lets also create a dataframe with data about where the clusters occur in the 5 component PCA space.
cluster_locs = pd.DataFrame(final_fit.cluster_centers_,columns=['component %s'% str(s) for s in range(np.size(final_fit.cluster_centers_,1))])

df.to_csv('cluster.csv')
