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
print len(players)


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
#print df
# df.to_csv('players.csv')

# for player in players:
# 	name = player['Name']
# 	overall = player['Overall']
df_noIDs = df.drop(['_id'],1)
print df_noIDs


# pd.options.display.mpl_style = 'default' #load matplotlib for plotting
# plt.style.use('ggplot') #im addicted to ggplot. so pretty.
# mpl.rcParams['font.family'] = ['Bitstream Vera Sans']

# df = pd.read_json("players.json")
# print df
# saveNames = df['Name']
# df = df.drop(['Name'],1)
# print df
