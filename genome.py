import numpy as np


class Genom():
    
    def __init__(self, n_In : int, n_Out : int) -> None:
        self.in_Nodes = [Node(i,type = "input") for i in range(n_In)]
        self.out_Nodes = [Node(i,type = "out") for i in range(n_Out)]
        self.hidden_Nodes = []
        self.connections = [Connection(self.in_Nodes[i],self.out_Nodes[j]) for i in range(n_In) for j in range(n_Out)]

    def p_connections(self):
        for c in self.connections:
            print(c.in_Node)
            print(c.in_Node)
        


class Connection():

    def __init__(self, in_Node, out_Node) -> None:
        self.in_Node = in_Node
        self.out_Node = out_Node
        self.weight = np.random.normal(0,1)


class Node():

    def __init__(self, key, type="hidden") -> None:
        self.key = key
        self.type = type
        self.bias = 0
