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


subgraphs = []
for i in range(len(subgraphs_nodes)):
    subgraph_cur = {}  # current subgraph (dict)
    for path in paths:  # iterate every edges of all graphs
        if path[0] in subgraphs_nodes[i]: # if current subgraph contains the node
            if path[0] in subgraph_cur:  # if dict already include
                subgraph_cur[path[0]].append((path[1], (path[2], path[3])))  # (name, (dir, dis)) <- viewed as weight
            else:  # otherwise initialize
                subgraph_cur[path[0]] = [(path[1], (path[2], path[3]))]
            if path[1] in subgraph_cur:  # undirected graph (so append the other way)
                subgraph_cur[path[1]].append((path[0], ((path[2]+math.pi)%(2*math.pi), path[3])))  # turn 180 deg
            else:
                subgraph_cur[path[1]] = [(path[0], ((path[2]+math.pi)%(2*math.pi), path[3]))]
    for key in subgraphs_nodes[i]:
        if key not in subgraph_cur:  # just in case there are empty ones
            subgraph_cur[key] = []
    subgraphs.append(subgraph_cur)


# for subgraph in subgraphs:
subgraph = subgraphs[0]
path_weights = dfs_findPath(subgraph, '大宛')
print(path_weights)
