# -*- coding: utf-8 -*-
"""
Created on Sun May 14 15:25:24 2023

@author: alexh
"""

import networkx as nx
import matplotlib.pyplot as plt

from sklearn.manifold import MDS
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

import numpy as np
import math

def calculate_bearing(coords_i, coords_j):
    lat1, lon1 = coords_i
    lat2, lon2 = coords_j
    dlon = (lon2 - lon1)
    dlat = lat2 - lat1
    bearing = math.atan2(dlon, dlat)  # atan2(y,x) =  arctan(y/x) get 方位角
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
            
missing_values = np.random.rand(n_cities, n_cities) < 0.3
distances_2 = distances.copy()
distances[missing_values] = np.nan



from scipy.optimize import least_squares

def triangulate(distances, bearings):
    # Iterate over all pairs of cities
    for i in range(len(distances)):
        for j in range(i+1, len(distances)):
            if i==j:
                distances[i,j] = 0
            if np.isnan(distances[i,j]) or np.isnan(bearings[i,j]):
                # Estimate missing distance and bearing using triangulation
                for k in range(len(distances)):
                    if k != i and k != j and not np.isnan(distances[i,k]) and not np.isnan(distances[j,k]) and not np.isnan(bearings[i,k]) and not np.isnan(bearings[j,k]):
                        # Calculate vector from city i to k
                        vec_i_to_k = distances[i,k] * np.array([np.cos(bearings[i,k]), np.sin(bearings[i,k])])

                        # Calculate vector from city j to k
                        vec_j_to_k = distances[j,k] * np.array([np.cos(bearings[j,k]), np.sin(bearings[j,k])])

                        # Define function to minimize
                        def func(x):
                            dist_i_to_x = np.linalg.norm(x - vec_i_to_k)
                            dist_j_to_x = np.linalg.norm(x - vec_j_to_k)
                            return np.array([distances[i,j] - dist_i_to_x - dist_j_to_x])

                        # Use least squares to minimize the function
                        try:
                            res = least_squares(func, np.zeros(2))

                            # Calculate estimated distance and bearing between i and j
                            dist_estimate = res.fun[0]
                            bearing_estimate = np.arctan2(res.x[1], res.x[0])
    
                            # Update matrices
                            distances[i,j] = dist_estimate
                            distances[j,i] = dist_estimate
                            bearings[i,j] = bearing_estimate
                            bearings[j,i] = bearing_estimate
                            break
                        except ValueError:
                            break
    return distances, bearings

distances_est, bearings_est = triangulate(distances.copy(), bearings)
for i in range(len(distances_est)):
    for j in range(len(distances_est)):
        if i>j:
            distances_est[i,j] = distances_est[j,i]
distances_est[np.isnan(distances_est)] = 0
# Calculate 2D coordinates using MDS algorithm
mds = MDS(n_components=2, dissimilarity='precomputed', random_state=45)
coords_2d = mds_coords = mds.fit_transform(distances_est)

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