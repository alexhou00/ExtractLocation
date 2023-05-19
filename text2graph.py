# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 11:10:54 2023

@author: alexh
"""

import matplotlib.pyplot as plt
import math
import csv
import re

import hashlib

import networkx as nx

# TO Do: unknown dis, unknown dir


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


def find_edge(data, match):
    for sublist in data:
        if sublist[:2] == list(match):
            return sublist[-1]
    return None

def hashColor(string_to_hash):
    # Define the string to hash and the maximum RGB value
    # string_to_hash = "hello world"
    max_rgb_value = 255
    if string_to_hash != None:
        # Hash the string using SHA-256 and convert the resulting hexadecimal string to an integer
        hashed_string = int(hashlib.sha256(string_to_hash.encode()).hexdigest(), 16)
        
        # Extract the red, green, and blue components from the hashed integer
        red = hashed_string % (max_rgb_value + 1)
        green = (hashed_string // (max_rgb_value + 1)) % (max_rgb_value + 1)
        blue = (hashed_string // ((max_rgb_value + 1) ** 2)) % (max_rgb_value + 1)
        
        # Create an RGB tuple using the extracted color components
        rgb_tuple = (red, green, blue)
        
        return rgb_tuple # Output: (190, 160, 205)
    else:
        return (0,0,0)

# MAIN CODE STARTS HERE
bookNum = 0
filenames = ['outputRGH0424_2_manual', 'outputBOH0424', 'outputBLH0424']
csvfilename = filenames[bookNum]
arr = []
# ref = []
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

	arr[i][0] = arr[i][0].replace('國','')
	arr[i][1] = arr[i][1].replace('國','')

	keep = False
	for j in arr[i][2]:
		if j in ('南', '北', '西', '東'): # if 方位 is correct
			keep = True
	"""
	if not arr[i][3][:-1].isnumeric(): # if 里程 is not number
		keep = False
	"""

	if not keep:
		rem.append(arr[i])
		continue

for i in rem: # remove invalid ones
	arr.remove(i)

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
            
	if re.match(r'\d+里', arr[i][3]): #arr[i][3].endswith('里') and arr[i][3][:-1].isnumeric():
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

conv = TtoG(paths)
conv.run()

print(arr)
arr = sorted(arr, key=lambda x: int(''.join([c for c in x[3] if c.isdigit()])) if ''.join([c for c in x[3] if c.isdigit()]) != '' else 0, reverse=True)

for g in (conv.graphs):
    print(g)



for n, pos in enumerate(conv.graphs):
    print("graph", n)
    # Create a graph
    G = nx.Graph()
    
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # Chinese fonts 
    
    
    # Define the positions of the nodes
    
    dict_pos = {}
    
    for inner_list in pos:
        key = inner_list[0]
        value = (round(inner_list[1], 1), round(inner_list[2], 1))
        dict_pos[key] = value
    
    # print(result_dict)
    
    # Add some nodes
    G.add_nodes_from(list(dict_pos.keys()))
    
    # Add edges
    edges = []
    for row in arr:
        if row[3].rstrip('里').isnumeric():
            edges.append((row[0], row[1], {'weight': row[3].rstrip('里')}))
        else:
            edges.append((row[0], row[1], {'weight': str(avg)}))
    cur_places = [i[0] for i in pos] # list of places names in the current graph

    # remove edges that is not in the current graph
    toRemove = []
    for i in edges:
        if not (i[0] in cur_places and i[1] in cur_places):
            toRemove.append(i)
    for i in toRemove: edges.remove(i)

    G.add_edges_from(edges)
    # G.add_edges_from([tuple(row[:2]) for row in unknownDis])
    

    # nx draw options
    options = {
        'node_color': 'white', # node color
        'node_size': 350, # node size
        'linewidths': 1, # node border width
        'edgecolors': 'black', # node border color
        'font_size': 6
        # 'edge_color': 'k',     # doesnt work idfk why   
    }
    
    # Draw the graph with custom node positions
    print(dict_pos)
    """
    fixed_pos = []
    for place in dict_pos:
        if not in Un"""
    # Fixed the fixed nodes and spring_layout the free ones (the ones without 里程)
    
    dict_pos = nx.spring_layout(G, pos=dict_pos, fixed=dict_pos.keys(), k=800, iterations=5)

    nx.draw(G, pos=dict_pos, with_labels=True, **options)
    # draw edges weights (length)
    edge_labels = {(u, v): d.get('weight') for u, v, d in G.edges(data=True) if int(d.get('weight')) != avg}
    nx.draw_networkx_edge_labels(G, pos=dict_pos, edge_labels=edge_labels, font_size=4)
    edge_color = [(find_edge(arr, match), hashColor(find_edge(arr, match))) for match in list(G.edges)]
    nx.draw_networkx_edges(G, pos=dict_pos, edge_color=[c[1] for c in edge_color])
    print(edge_color)
    

    # Show the graph
    ax = plt.gca() # gca: Get Current Axis
    ax.margins(0.15)  # leave margin to prevent node got cut
    plt.axis("equal") # x and y axis to be same scale
    #fig = plt.gcf()  # so that I can both show and save fig (current fig will reset)
    #plt.show() # no need if plotting in the Plots pane
    plt.savefig(f'plt/{csvfilename}_{n}.png', dpi=2400) # save figure; resolution=1200dpi
    plt.clf()  # clear figure, to tell plt that I'm done with it (use when saving figs)
    # font-path -> "C:\Users\<username>\miniconda3\envs\spyder-env\Lib\site-packages\matplotlib\mpl-data"