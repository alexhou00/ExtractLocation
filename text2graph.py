# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 11:10:54 2023

@author: alexh
"""

import matplotlib.pyplot as plt
import math
import csv

import networkx as nx

# TO Do: 國、unknown dis, unknown dir, 數千里


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
	def dfs(self,now,pos):
		if not now in self.done:
			self.graphs[-1].append([now,pos[0],pos[1]])
		else:
			return
		self.done.append(now);
		for i in range(len(self.edges)):
			nxt = ""
			delta = []
			if self.edges[i][1] == now:
				nxt = self.edges[i][0]
				delta = [self.edges[i][2],self.edges[i][3]]
			elif self.edges[i][0] == now:
				nxt = self.edges[i][1]
				delta = [self.edges[i][2]+math.pi,self.edges[i][3]];
			else:
				continue
			nxtpos = [pos[0]+delta[1]*math.cos(delta[0]),pos[1]+delta[1]*math.sin(delta[0])]
			self.dfs(nxt,nxtpos)
		return

	def run(self):
		edges = self.edges
		self.graphs = []
		self.done = []
		for i in range(len(edges)):
			if edges[i][0] not in self.done:
				self.graphs.append([])
				self.dfs(edges[i][0],[0,0])
		return
# return 3d list as [[[name1,x1,y1],[name2,x2,y2],[name3,x3,y3]],
#                   [[nname1,xx1,yy1],[nname2,xx2,yy2]]]


# main code starts here

arr = []
with open('outputRGH0424_2_manual_bruh.csv', newline='', encoding='utf-8') as csvfile:
	rows = csv.reader(csvfile)
	for row in rows:
		arr.append([row[0],row[1],row[2],row[3]])
arr.remove(arr[0])

rem = []  # to remove
for i in range(len(arr)):
	if any('-' in sub for sub in arr[i]):
		rem.append(arr[i])
		continue
	arr[i][0] = arr[i][0].replace("國",'')
	arr[i][1] = arr[i][1].replace("國",'')

	keep = False
	for j in arr[i][2]:
		if j in ('南', '北', '西', '東'):
			keep = True
	if not arr[i][3][:-1].isnumeric():
		keep = False
	if not keep:
		rem.append(arr[i])
		continue

for i in rem:
	arr.remove(i)

paths = []
for i in range(len(arr)):
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
	r = int(arr[i][3][:-1]);
	tx = 0
	ty = math.pi/2
	if dx<0:
		tx = math.pi
	if dy<0:
		ty *= 3
	theta = 0
	if abs(dx)+abs(dy) != 0:
		theta = tx*abs(dx)+ty*abs(dy);
		theta /= abs(dx)+abs(dy)
	paths.append([arr[i][0],arr[i][1],theta,r])
conv = TtoG(paths)
conv.run()

print(arr)
print()
for g in (conv.graphs):
    print(g)




for pos in conv.graphs:
    # Create a graph
    G = nx.Graph()
    
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # Chinese fonts 
    
    
    
    # Define the positions of the nodes
    # pos = conv.graphs[0] #{1: (0, 0), 2: (1, 1), 3: (2, 0), 4: (1, -1)}
    
    dict_pos = {}
    
    for inner_list in pos:
        key = inner_list[0]
        value = (round(inner_list[1], 1), round(inner_list[2], 1))
        dict_pos[key] = value
    
    # print(result_dict)
    
    # Add some nodes
    G.add_nodes_from(list(dict_pos.keys()))
    
    from matplotlib.font_manager import FontProperties
    font = FontProperties(fname=r"C:\Alex\Fonts\Google\Noto_Sans_TC\NotoSansTC-Regular.otf", size=12)
    
    options = {
        'node_color': 'white', # node color
        'node_size': 800, # node size
        'linewidths': 1, # node border width
        'edgecolors': 'black', # node border color
        # 'edge_color': 'k',     # doesnt work idfk why   
    }
    # Draw the graph with custom node positions
    nx.draw(G, pos=dict_pos, with_labels=True, **options) #, font_family=font.get_name(), font_size=12)
    

    # Show the graph
    ax = plt.gca()
    ax.margins(0.15)  # leave margin to prevent node got cut
    plt.axis("off")
    plt.show()
    
    # font-path -> "C:\Users\alexh\miniconda3\envs\spyder-env\Lib\site-packages\matplotlib\mpl-data"