# -*- coding: utf-8 -*-
"""
Created on Sun May 14 15:25:24 2023

@author: alexh
"""

import networkx as nx
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
import numpy as np
import math

def calculate_bearing(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dLon = lon2 - lon1
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    return bearing

city_names = ['A', 'B', 'C', 'D', 'E']
coords = [
         [37.7749, -122.4194], # 假定城市A的經緯度
         [34.0522, -118.2437], # 假定城市B的經緯度
         [29.7604, -95.3698], # 假定城市C的經緯度
         [40.7128, -74.0060], # 假定城市D的經緯度
         [41.8781, -87.6298] # 假定城市E的經緯度
         ]

# 計算距離和方位角
n_cities = len(city_names)
distances = np.zeros((n_cities, n_cities))
bearings = np.zeros((n_cities, n_cities))

for i in range(n_cities):
    for j in range(n_cities):
        if i != j:
            distances[i, j] = np.linalg.norm(np.array(coords[i]) - np.array(coords[j]))
            bearings[i, j] = calculate_bearing(coords[i], coords[j])
            
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

# Create a distance matrix with missing data
n_cities = len(city_names)
missing_values = np.random.rand(n_cities, n_cities) < 0.3
distances[missing_values] = np.nan
# Fill in missing values with mean distance
imputer = SimpleImputer(strategy='mean')
distances = imputer.fit_transform(distances)
# Calculate 2D coordinates using PCA algorithm
pca = PCA(n_components=2, svd_solver='full')
coords_2d = pca_coords = pca.fit_transform(distances)
"""
# Calculate PCA coordinates
pca = PCA(n_components=2)
features = np.hstack((distances.reshape(-1, 1), bearings.reshape(-1, 1)))
coords_2d = pca_coords = pca.fit_transform(features)"""

"""
# Calculate 2D coordinates using MDS algorithm
mds = MDS(n_components=2, dissimilarity='precomputed', random_state=45)
coords_2d = mds_coords = mds.fit_transform(distances)"""
"""
# Correct MDS coordinates according to bearing (方位角)
coords_2d = np.zeros_like(mds_coords)
for i, city1 in enumerate(city_names):
    for j, city2 in enumerate(city_names):
        if i < j:
            bearing = bearings[i, j]
            bearing_rad = math.radians(bearing)
            rotation_matrix = np.array([[math.cos(bearing_rad), -math.sin(bearing_rad)],
                                        [math.sin(bearing_rad), math.cos(bearing_rad)]])
            coords_2d[j] = np.dot(rotation_matrix, mds_coords[j])"""
"""
# Calculate 2D coordinates using MDS algorithm with interpolation
def mds_interpolate(distances, bearings, city_names):
    
    distances[1][1] = np.nan
    distances[2][3] = np.nan
    
    # Calculate initial MDS coordinates
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    mds_coords = mds.fit_transform(distances)
    
    
    # MDS interpolation
    for i, city1 in enumerate(city_names):
        for j, city2 in enumerate(city_names):
            if i < j:
                if np.isnan(distances[i, j]) or np.isnan(bearings[i, j]):
                    # Interpolate missing distance and bearing values
                    d = np.sqrt(np.sum((mds_coords[i] - mds_coords[j]) ** 2))
                    b = math.degrees(math.atan2(mds_coords[j][1] - mds_coords[i][1], mds_coords[j][0] - mds_coords[i][0]))
                    if np.isnan(distances[i, j]):
                        distances[i, j] = d
                        distances[j, i] = d
                    if np.isnan(bearings[i, j]):
                        bearings[i, j] = b
                        bearings[j, i] = b
    
    # Correct MDS coordinates according to bearing
    coords_2d = np.zeros_like(mds_coords)
    for i, city1 in enumerate(city_names):
        for j, city2 in enumerate(city_names):
            if i < j:
                bearing = bearings[i, j]
                bearing_rad = math.radians(bearing)
                rotation_matrix = np.array([[math.cos(bearing_rad), -math.sin(bearing_rad)],
                                            [math.sin(bearing_rad), math.cos(bearing_rad)]])
                coords_2d[j] = np.dot(rotation_matrix, mds_coords[j])
    return mds_coords #coords_2d

coords_2d = mds_interpolate(distances, bearings, city_names)
"""
# 創建一個空的無向圖
G = nx.Graph()

# 添加城市節點和距離邊
for city in city_names:
    G.add_node(city)

for i, city1 in enumerate(city_names):
    for j, city2 in enumerate(city_names):
        if i < j:
            G.add_edge(city1, city2, distance=distances[i, j])

# 繪製圖形
pos = {city: coords_2d[index] for index, city in enumerate(city_names)}
nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=12, font_weight='bold')

# 添加邊的標籤（距離）
edge_labels = {(city1, city2): round(G.edges[city1, city2]['distance'], 2) for city1, city2 in G.edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)

# 顯示圖形
plt.show()