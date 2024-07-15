import os
import time
import copy
import datetime
import json
import torch
import collections
from sklearn.model_selection import train_test_split

def load_graph(path = None, num_files = None, steps = 101):
    os.chdir(path)
    files = os.listdir(path)
    
    data = []
    graph = collections.namedtuple('graph', ['edge_index', 'node_features',
                                             'edge_features',
                                             'connectivity'])
    # print('Loading Files')
    for geomind in range(num_files):
        
        with open('coords'+'.txt') as json_file:
            coords = json.load(json_file)
        # coords = np.array(coords)        
        coords = torch.tensor(coords)
        coords = coords[:,:2]
        
        with open('param'+'.txt') as json_file:
            node_param = json.load(json_file)
        node_param = torch.tensor(node_param)
        node_param = node_param.unsqueeze(0)
        # Repeat node_param for each row in coords
        node_param_expanded = node_param.repeat(coords.size(0), 1)
        with open('edge_index'+'.txt') as json_file:
            edge_index = json.load(json_file)
        # edge_index = np.array(edge_index)
        edge_index = torch.tensor(edge_index)
        
        with open('connectivity'+'.txt') as json_file:
            elements = json.load(json_file)
        # elements = np.array(elements)
        elements = torch.tensor(elements)
        
        # print(f'{geomind}/{num_files}')
        # Compute edge_features from nodal coordinates        
        for i in range(0,edge_index.size(0)):            
            xij = coords[edge_index[i][0]-1,:] - coords[edge_index[i][1]-1,:]
            
            mod_xij = torch.linalg.norm(xij).view(1)
            
            tmp = torch.cat((xij,mod_xij)).view(1,3)            
            
            if i==0:
                edge_features = torch.clone(tmp)
            else:                
                edge_features = torch.cat((edge_features, tmp),dim=0)
        
        # Concatenate node features without BCs
        node_features = torch.cat([coords, node_param_expanded], dim=1)                    
                            
        # Create a collection with graph elements
        tmp = graph(edge_index.t(), node_features, edge_features,
                    elements)        
                
        data.append(tmp)
    return data