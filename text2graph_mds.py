# -*- coding: utf-8 -*-
"""
Created on Thu May 18 00:20:09 2023

@author: alexh
"""

import matplotlib.pyplot as plt
import networkx as nx

import math
import csv
import re

from sklearn.manifold import MDS
import numpy as np
from scipy.optimize import minimize_scalar

from collections import deque

# Todo: 使用 MDS 中的 dissimilarity='euclidean' (再算方位角旋轉整體)
# → 套用至西域：選擇有長度有方位者，用 DFS 推出兩兩間距離 → 作 MDS →  找最小誤差的角度旋轉/翻轉整體 → 補上其他邊、點 → 微調位置

class TtoG: # text to graph
    edges = []
    done = []
    graphs = []
# a 2d list as [[pos1,pos2,dir(radius),len]]

    # initialize edges
    def __init__(self,inp):
        self.edges = inp
        return

    # dfs implementation
    def dfs(self,now):
        if not now in self.done:
            self.graphs[-1].append(now)
        else:
            return
        self.done.append(now);
        for i in range(len(self.edges)):
            nxt = ""
            if self.edges[i][1] == now:
                nxt = self.edges[i][0]
            elif self.edges[i][0] == now:
                nxt = self.edges[i][1]
            else:
                continue
            self.dfs(nxt)
        return
    
    # run table to graph function (activate dfs)
    def run(self):
        edges = self.edges
        self.graphs = []
        self.done = []
        for i in range(len(edges)):
            if edges[i][0] not in self.done:
                self.graphs.append([])
                self.dfs(edges[i][0]) #,[0,0])
        
        # return 3d list as [[[name1,x1,y1],[name2,x2,y2],[name3,x3,y3]],
        #                   [[nname1,xx1,yy1],[nname2,xx2,yy2]]]
        return


def readfile(bookNum):
    arr = []
    # ref = []
    filenames = ['outputRGH0424_2_manual', 'outputBOH0424', 'outputBLH0424']
    csvfilename = filenames[bookNum]
    # open csv file and read
    with open(csvfilename+".csv", newline='', encoding='utf-8') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            arr.append([row[0],row[1],row[2],row[3], row[4]])
            # ref.append([row[0],row[1],row[2],row[3],row[4]])
    arr.remove(arr[0]) # remove header row
    # ref.remove(ref[0]) # remove header row
    
    rem = []  # to remove
    for i in range(len(arr)-1):
        if any('-' in sub for sub in arr[i][:-1]):
            rem.append(arr[i])
            continue
        # remove the 國 character
        arr[i][0] = arr[i][0].replace('國','')
        arr[i][1] = arr[i][1].replace('國','')
    
        keep = False
        for j in arr[i][2]:
            if j in ('南', '北', '西', '東'): # if 方位 is correct
                keep = True
    
        if not keep:
            rem.append(arr[i])
            continue
    
    for i in rem: # remove invalid ones
        arr.remove(i)
    
    return arr

def table2paths(arr):
    # Calculate default length
    avg = [int(i[3].rstrip('里')) for i in arr if i[3].rstrip('里').isnumeric()]
    avg = sum(avg)//len(avg)
    
    # Process every row (table to list (with direction))
    paths = []
    unknownDis = []
    for i in range(len(arr)-1):
        dx = 0
        dy = 0
        for j in arr[i][2]:
            if j == '南':
                dy-=1
            elif j == '北':
                dy+=1
            elif j == '西':
                dx-=1
            elif j == '東':
                dx+=1
                
        if re.match(r'\d+里', arr[i][3]):
            r = int(arr[i][3].rstrip('里'))
        else:
            unknownDis.append(arr[i])        
            r = avg
    
        tx = 0
        ty = math.pi/2
        if dx<0:
            tx = math.pi
        if dy<0:
            ty *= 3
        theta = 0
        if abs(dx)+abs(dy) != 0:
            theta = tx*abs(dx)+ty*abs(dy)
            theta /= abs(dx)+abs(dy)
        paths.append([arr[i][0], arr[i][1], theta, r])
    return paths

def dfs_findPath(graph, start, visited=None, path=None, path_weights=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []
    if path_weights is None:
        path_weights = {}

    visited.add(start)
    path.append(start)

    for neighbor, weight in graph[start]:
        if neighbor not in visited:
            path_weights[neighbor] = path_weights.get(start, []) + [weight]
            dfs_findPath(graph, neighbor, visited, path, path_weights)

    return path_weights


def bfs_findPath(graph, start):
    queue = deque([(start, [])])  # Each item in the queue is a tuple (node, weight)
    path_weights = {start: []}

    while queue:
        node, weight = queue.popleft()

        for neighbor, edge_weight in graph[node]:
            if neighbor not in path_weights:
                queue.append((neighbor, weight + [edge_weight]))
                path_weights[neighbor] = weight + [edge_weight]

    return path_weights

def pathWeights2euDis(pathw):
    # list of path: (dir, dis) to euclidean distance
    path_weights = {}
    for k, v in pathw.items():
        x = sum(d * math.cos(theta) for (theta, d) in v)
        y = sum(d * math.sin(theta) for (theta, d) in v)
        path_weights[k] = math.sqrt(x**2 + y**2)
    return path_weights

def calculate_bearing(coords_i, coords_j):
    lat1, lon1 = list(coords_i)
    lat2, lon2 = list(coords_j)
    dlon = (lon2 - lon1)
    dlat = lat2 - lat1
    bearing = math.atan2(dlon, dlat)  # atan2(y,x) =  arctan(y/x) get 方位角
    # bearing = math.degrees(bearing)

    return bearing

def find_optimal_theta(n_cities, G, pos, paths):
    bearings = np.zeros((n_cities, n_cities))
    bearings = {}
    for city1, city2 in list(G.edges):
        bearings[(city1, city2)] = calculate_bearing(pos[city1], pos[city2]) % math.pi
    
    bearings_actual = {}
    for path in paths:
        node1, node2, angle, distance = path
        bearings_actual[(node1, node2)] = angle % math.pi
    
    bearings_arr = []
    bearings_actual_arr = []
    bearings_keys = []
    for k, v in bearings.items():
        (node1, node2) = k
        bearings_keys.append(tuple(sorted([node1, node2])))
        bearings_arr.append(v)
        if (node1, node2) in bearings_actual:
            bearings_actual_arr.append(bearings_actual[(node1, node2)])
        else: #or (node2, node1) in 
            bearings_actual_arr.append(bearings_actual[(node2, node1)])
            
    
    bearings_actual_arr = np.array(bearings_actual_arr)
    bearings_arr = np.array(bearings_arr)
    # Compute the error function for a given constant theta
    def error(theta):
        return np.sum(abs(bearings_arr + theta - bearings_actual_arr)**2)
    
    # Use scipy.optimize.minimize_scalar to find the minimum error and corresponding theta
    result = minimize_scalar(error)
    optimal_theta = result.x
    minimum_error = result.fun
    return optimal_theta, minimum_error



# MAIN CODE STARTS HERE

# bookNum 史記 0; 漢書 1; 後漢書 2
bookNum = 0

# read every row of table to list
arr = readfile(bookNum)

# convert raw list data to graph edges
paths = table2paths(arr)

# find 連通塊 (subgraph) and get nodes of each 連通塊
conv = TtoG(paths)  # TtoG object
conv.run()  # run dfs
subgraphs_nodes = conv.graphs  # list of all nodes of each subgraph

# create adjecency lists
subgraphs = []
for i in range(len(subgraphs_nodes)):
    subgraph_cur = {}  # current subgraph (dict)
    for path in paths:  # iterate every edges of all graphs
        node1, node2, angle, distance = path
        if node1 in subgraphs_nodes[i]: # if current subgraph contains the node
            if node1 in subgraph_cur:  # if dict already include
                subgraph_cur[node1].append((node2, (angle, distance)))  # (name, (dir, dis)) <- viewed as weight
            else:  # otherwise initialize
                subgraph_cur[node1] = [(node2, (angle, distance))]
            if node2 in subgraph_cur:  # undirected graph (so append the other way)
                subgraph_cur[node2].append((node1, ((angle+math.pi)%(2*math.pi), distance)))  # turn 180 deg
            else:
                subgraph_cur[node2] = [(node1, ((angle+math.pi)%(2*math.pi), distance))]
    for key in subgraphs_nodes[i]:
        if key not in subgraph_cur:  # just in case there are empty ones
            subgraph_cur[key] = []
    subgraphs.append(subgraph_cur)


# for subgraph in subgraphs:
    
subgraph = subgraphs[0] ###
subgraph = dict(sorted(subgraph.items(), key=lambda x:x[0]))

n_cities = len(subgraph)
distances = np.empty((n_cities, n_cities))

for i, start_node in enumerate(subgraph):
    path_weights = bfs_findPath(subgraph, start_node)
    # print(path_weights)
    
    path_len = pathWeights2euDis(path_weights)
    
    path_len = sorted(path_len.items(), key=lambda x:x[0])

    distances[i] = np.array([p[1] for p in path_len])


mds = MDS(n_components=2, dissimilarity='euclidean', random_state=42, 
          n_init=400, max_iter=300, normalized_stress=False)
coords_2d = mds_coords = mds.fit_transform(distances)

G = nx.Graph()

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # Chinese fonts

# 添加城市節點和距離邊
for city in subgraph.keys():
    G.add_node(city)

edge_labels = {}
for i, (city1, v) in enumerate(subgraph.items()):
    edges2city1 = [row[0] for row in v]
    for j, city2 in enumerate(subgraph.keys()):
        if city2 in edges2city1:
            G.add_edge(city1, city2, distance=distances[i, j])
            edge_labels[(city1, city2)] = round(G.edges[city1, city2]['distance'])

pos = {city: coords_2d[index] for index, city in enumerate(subgraph.keys())}

# Deal with Rotation



optimal_theta, minimum_error = find_optimal_theta(n_cities, G, pos, paths)
pos_flipped = {}
for k, v in pos.items():
    pos_flipped[k] = np.copy(v)
    pos_flipped[k][0] *= -1
optimal_theta_flipped, minimum_error_flipped = find_optimal_theta(n_cities, G, pos_flipped, paths)
if minimum_error_flipped < minimum_error:
    optimal_theta = optimal_theta_flipped
    pos = pos_flipped
rotation_matrix = np.array([[math.cos(optimal_theta), -math.sin(optimal_theta)],
                            [math.sin(optimal_theta), math.cos(optimal_theta)]])

# 繪製圖形
# nx draw options
options = {
    'node_color': 'white', # node color
    'node_size': 350, # node size
    'linewidths': 1, # node border width
    'edgecolors': 'black', # node border color
    'font_size': 6
    # 'edge_color': 'k',     # doesnt work idfk why   
}
pos_rotated = pos.copy()
for k, P in pos.items():
    pos_rotated[k] = np.dot(P, rotation_matrix)
    
nx.draw(G, pos_rotated, with_labels=True, **options)

# 添加邊的標籤（only known 距離）
nx.draw_networkx_edge_labels(G, pos_rotated, edge_labels=edge_labels, font_size=4)


# 顯示圖形
ax = plt.gca() # gca: Get Current Axis
ax.margins(0.15)  # leave margin to prevent node got cut
plt.axis("equal") # x and y axis to be same scale
#fig = plt.gcf()  # so that I can both show and save fig (current fig will reset)
#plt.show() # no need if plotting in the Plots pane
plt.savefig('plt/test.png', dpi=2400) # save figure; resolution=1200dpi
plt.clf()  # clear figure, to tell plt that I'm done with it (use when saving figs)
# font-path -> "C:\Users\<username>\miniconda3\envs\spyder-env\Lib\site-packages\matplotlib\mpl-data"