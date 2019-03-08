'''
Implement a method/function which takes a matrix representation of a DAG as input, along with a d-seperation query, 
and outputs a value TRUE or FALSE.

This matrix represents a DAG in the following way: if Xi --> Xj then the ij entry is 1, otherwise it is 0. Your function should 
come with an executable file which takes the matrix as input, along with a query of the form: number number list, 
Returns TRUE iff the variables corresponding to those numbers are d-separated given the numbers in list.

'''
import numpy as np
import pandas as pd
import argparse
import copy

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=False, help='Input DAG file')
    parser.add_argument('--q', required=False, type=int, nargs='+', help='Query in the form: start end | [list of observed variables]')

    args = parser.parse_args()

    return args

class Node:
    def __init__(self, name):
        '''
        A Node has 3 attributes:
        1. Value.
        2. A dictionary containing its parents.
        3. A dictionary containing its children.
        '''
        self.name=name
        self.parents=[]
        self.children=[]
        
        
def form_edges(lines):
    num=lines.shape[0]
    all_nodes=[Node(i) for i in range(num)]
    edges = list(map(lambda e: (int(e[0]), int(e[1])), zip(*(np.asarray(lines).nonzero())))) #list of all the edges
    for i in range(len(edges)):
        m, n= edges[i] #obtain tuples for every edge represented as (start, end)
        #set parents and chidlren based on edge value
        all_nodes[m].children.append(Node(n)) 
        all_nodes[n].parents.append(Node(m))
    return(all_nodes) #contains information about all the nodes in the graph

def decrease_by_1(starting_index, arr):
    if starting_index!=0:
        arr[0]-=1
        arr[1]-=1
        arr[2]=list(np.array(arr[2]) - 1)
        return (arr[0],arr[1], arr[2])
    

def d_sep(all_nodes, starting_index, query):
    start, end, observed=decrease_by_1(starting_index, query)
    
    visit_nodes = copy.copy(observed) # keep track of the nodes visited from the observed nodes
    obs_anc = set() # observed nodes and their ancestors

    # repeatedly visit the observed nodes' parents/ancestors
    while len(visit_nodes) > 0:
        next_node = visit_nodes.pop()
        for parent in all_nodes[next_node].parents:
            obs_anc.add(parent)
    
    trail = [(start, "up")] # store direction of movement to detect v-structures, if present
    visited = set() # keep track of visited nodes to avoid cyclic paths
    while len(trail) > 0:    
        (val, direction) = trail.pop() 
        node = all_nodes[val]

        # only visit nodes not previously visited
        if (val, direction) not in visited:
            visited.add((val, direction)) 

            # if trail becomes empty, then the nodes are not d-separated
            if val not in observed and val == end:
                 return False

            #traversing from children --> never an active trail
            if direction == "up" and val not in observed:
                for parent in node.parents:
                    trail.append((parent.name, "up"))
                for child in node.children:
                    trail.append((child.name, "down"))
            
            #traversing from parents
            elif direction == "down":
                # path to children is always active
                if val not in observed: 
                    for child in node.children:
                        trail.append((child.name, "down"))
                # path to parent forms a v-structure
                if val in observed or val in obs_anc: 
                    for parent in node.parents:
                        trail.append((parent.name, "up"))

    return True
    

def main():
    args=get_args()
    if args.input:
        lines=np.genfromtxt(args.input, skip_header=1)
    else:
        lines=np.genfromtxt('dag.txt', skip_header=1)
    starting_index=lines[0,0]
    lines=np.array(lines[:, 1:])
    
    m, n= lines.shape
    if m != n:
        print("Provided adjacency matrix is not a square one!")
    
    query=[]
    output=[]
    if args.q:
        if len(args.q)<3:
            print("A minimum of 3 arguments needed!")      
        temp=args.q
        query.append([temp[0], temp[1], temp[2:]])
    else:
        query.append([61, 68, [4, 19, 90]])
        query.append([55, 27, [4, 8, 9, 12, 29, 32, 40, 44, 45, 48, 50, 52]])

    all_nodes=form_edges(lines)
    for i in range(len(query)):
        output.append(d_sep(all_nodes, starting_index, query[i]))
        print(str(output[i]).upper())
    

if __name__ == "__main__":
    main()


