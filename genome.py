import numpy as np
import networkx as nx
import copy


class Genom():
    
    #init a new Genom
    def __init__(self, n_In : int, n_Out : int) -> None:
        self.in_Nodes = [Node(i,type = "input") for i in range(-n_In,0)]
        self.out_Nodes = [Node(i,type = "out") for i in range(n_Out)]
        self.hidden_Nodes = []
        self.connections = [Connection(self.in_Nodes[i],self.out_Nodes[j]) for i in range(n_In) for j in range(n_Out)]
        self.n_nodes = n_Out
    
    #create/overrite the Genom with given params
    def create(self,in_Nodes, out_Nodes,hidden_Nodes,connections):
        self.in_Nodes = in_Nodes,
        self.out_Nodes = out_Nodes
        self.hidden_Nodes = hidden_Nodes
        self.connections = connections
        self.n_nodes = len(self.out_Nodes) + len(self.hidden_Nodes)

    #forwardpass for the Genom
    def forward(self,x):
        if len(x) != len(self.in_Nodes):
            return
        
        #Queue structure to implement depth search
        queue = [(i,x[i+len(self.in_Nodes)]) for i in range(-len(self.in_Nodes),0,1)]
        #print("Queue: " +str(queue))
        output = []
        while len(queue) != 0:
            #print("Queue: " + str(queue))
            element = queue.pop()
            #print("Queue after pop: " + str(queue))
            for c in self.connections:
                if c.in_Node.key == element[0] and c.is_active: #only active connections
                    if c.out_Node in self.out_Nodes:
                        output.append((c.out_Node.key,element[1]*c.weight))
                    else:
                        queue.append((c.out_Node.key,element[1]*c.weight))

        #adding the tuple values together (for the same node)
        dic = dict()
        for key, value in output:
            if dic.get(key):
                dic.update([(key,dic.get(key)+value)])
            else:
                dic.update([(key,value)])

        output = list(dic.items())
        return output
    
    #Print the connections
    def p_connections(self):
        print("===== Connections =====")
        for c in self.connections:
            c.p_con()
        print("")

    #print the nodes
    def p_nodes(self):
        print("===== Input Nodes =====")
        for n in self.in_Nodes:
            n.p_node()

        print("===== Hidden Nodes =====")
        for n in self.hidden_Nodes:
            n.p_node()

        print("===== Output Nodes =====")
        for n in self.out_Nodes:
            n.p_node()

        print("")
    
    #creates a graph of the genom
    def create_Graph(self):
        G = nx.DiGraph()
        G.add_nodes_from([n.key for n in self.in_Nodes])
        G.add_nodes_from([n.key for n in self.hidden_Nodes])
        G.add_nodes_from([n.key for n in self.out_Nodes])

        edges = []
        for c in self.connections:
            if c.is_active:
                edges.append((c.in_Node.key,c.out_Node.key,round(c.weight,2)))
        G.add_weighted_edges_from(edges)       
        return G
    
    #draw the graph
    def visualize(self, labels = True, color = "blue"):
        G = self.create_Graph()
        
        pos = nx.spring_layout(G)
        nx.draw(G,pos=pos,with_labels = True, node_color = color)
        if labels:
            edge_labels = nx.get_edge_attributes(G, "weight")
            nx.draw_networkx_edge_labels(G, pos, edge_labels, verticalalignment="bottom", font_size=10)

    #checks either con is in self.connection or not
    def has_connection(self,con):
        for c in self.connections:
            if c.in_Node.key == con.in_Node.key and c.out_Node.key == con.out_Node.key:
                return True
        return False

    #mutates the genom
    def mutate(self, alpha=0.1):

        #mutate every weigth
        for c in self.connections:
            c.weight += alpha*np.random.normal(0,1)

        #adding a new Node
        new_connections = []
        for c in self.connections:
            #probability 10% for ech connection
            if np.random.rand(1) < 0.05:
                new_Node = Node(self.n_nodes)
                self.hidden_Nodes.append(new_Node)
                new_connections.append(Connection(c.in_Node,new_Node, weight=1))
                new_connections.append(Connection(new_Node,c.out_Node, weight = c.weight))
                self.n_nodes += 1
                c.disable() 

        self.connections += new_connections

        #adding new connections between input nodes and hidden nodes
        for iN in self.in_Nodes:
            for hN in self.hidden_Nodes:
                if np.random.rand(1) < 0.01:
                    new_connection = Connection(iN,hN)
                    if not self.has_connection(new_connection):
                        self.connections.append(new_connection)
                        #if this change result into a cycle -> delete the node again
                        try:
                            G = self.create_Graph()
                            nx.find_cycle(G)
                            self.connections.remove(new_connection)
                        except:
                            pass

        #adding new connections between two hidden nodes
        for hN1 in self.in_Nodes:
            for hN2 in self.hidden_Nodes:
                if np.random.rand(1) < 0.01:
                    new_connection = Connection(hN1,hN2)
                    if not self.has_connection(new_connection):
                        self.connections.append(new_connection)
                        #if this change result into a cycle -> delete the node again
                        try:
                            G = self.create_Graph()
                            nx.find_cycle(G)
                            self.connections.remove(new_connection)
                        except:
                            pass

        #adding new connections between output nodes and hidden nodes          
        for hN in self.in_Nodes:
            for oN in self.hidden_Nodes:
                if np.random.rand(1) < 0.01:
                    new_connection = Connection(hN,oN)
                    if not self.has_connection(new_connection):
                        self.connections.append(new_connection)
                        #if this change result into a cycle -> delete the node again
                        try:
                            G = self.create_Graph()
                            nx.find_cycle(G)
                            self.connections.remove(new_connection)
                        except:
                            pass
        #double check
        try:
            G = self.create_Graph()
            nx.find_cycle(G)
            print("Mistakes happend")
        except:
            pass


class Connection():

    #init a connection
    def __init__(self, in_Node, out_Node, weight = None) -> None:
        self.in_Node = in_Node
        self.out_Node = out_Node
        self.weight = weight or np.random.normal(0,1)
        self.is_active = True

    #prints itself
    def p_con(self):
        print(str(self.in_Node.key) +" --> " + str(self.out_Node.key),end=" ")
        print("Weight: " + str(self.weight),end=" ")
        print("is active : " + str(self.is_active))

    #disable the connection
    def disable(self):
        self.is_active = False
    
    #enable the connection
    def enable(self):
        self.is_active = True


class Node():
    #init a Node
    def __init__(self, key, type="hidden") -> None:
        self.key = key
        self.type = type
        self.bias = 0
    #print the node
    def p_node(self):
        print("Key: " + str(self.key),end=" ")
        print("Type: " + str(self.type),end=" ")
        print("Bias: " + str(self.bias))