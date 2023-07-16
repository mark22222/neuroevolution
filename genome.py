import numpy as np
import networkx as nx
import copy


class Genom():
    
    #init a new Genom
    def __init__(self, n_In : int, n_Out : int) -> None:
        self.in_Nodes = [Node(i,type = "input") for i in range(-n_In,0)]
        self.out_Nodes = [Node(i,type = "output") for i in range(n_Out)]
        self.hidden_Nodes = []
        self.connections = [Connection(self.in_Nodes[i],self.out_Nodes[j]) for i in range(n_In) for j in range(n_Out)]
        self.n_nodes = n_Out 

    
    #returns true if node is in out_Nodes
    def is_outNode(self,node):
        for n in self.out_Nodes:
            if n.key == node.key:
                return True
        return False

    #forwardpass for the Genom
    def forward(self,x):

        if len(x) != len(self.in_Nodes):
            return
        
        #stack structure to implement depth search
        stack = [(i,x[i+len(self.in_Nodes)] + self.in_Nodes[i+len(self.in_Nodes)].bias) for i in range(-len(self.in_Nodes),0,1)]
        output = [(i,0) for i in range(len(self.out_Nodes))]

        while len(stack) != 0:

            element = stack.pop()
            
            for c in self.connections:
                if c.in_Node.key == element[0] and c.is_active: #only active connections
                    if self.is_outNode(c.out_Node):
                       
                        output.append((c.out_Node.key,element[1]*c.weight))
                    else:
                        stack.append((c.out_Node.key,element[1]*c.weight + c.out_Node.bias))

        #adding the tuple values together (for the same node)
        dic = dict()
        for key, value in output:
            if dic.get(key):
                dic.update([(key,dic.get(key)+value)])
            else:
                dic.update([(key,value)])

        output = list(dic.items())
        
        for i in range(len(output)):
            tmp = output[i]
            newTuple = (tmp[0],tmp[1]+self.in_Nodes[tmp[0]].bias)
            output[i] = newTuple
    
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
    def visualize(self, labels = True, color = "green"):
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
    def mutate(self, new_node_prob=0.03, new_con_prob = 0.05, alpha=0.1):

        #mutate every weigth
        for c in self.connections:
            if np.random.rand(1) < 0.8:
                c.weight += alpha*np.random.normal(0,1)

        for n in self.in_Nodes:
            if np.random.rand(1) < 0.8:
                n.bias += alpha*np.random.normal(0,1)

        for n in self.hidden_Nodes:
            if np.random.rand(1) < 0.8:
                n.bias += alpha*np.random.normal(0,1)

        for n in self.out_Nodes:
            if np.random.rand(1) < 0.8:
                n.bias += alpha*np.random.normal(0,1)

        #adding a new Node
        new_connections = []
        for c in self.connections:
            if np.random.rand(1) < new_node_prob:
                new_Node = Node(self.n_nodes)
                self.hidden_Nodes.append(new_Node)
                new_connections.append(Connection(c.in_Node,new_Node, weight=1) )
                new_connections.append(Connection(new_Node,c.out_Node, weight = c.weight))
                c.disable()
                self.n_nodes += 1
                
        self.connections += new_connections

        #adding new connections between input nodes and hidden nodes
        for iN in self.in_Nodes:
            for hN in self.hidden_Nodes:
                if np.random.rand(1) < new_con_prob:
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
        for hN1 in self.hidden_Nodes:
            for hN2 in self.hidden_Nodes:
                if np.random.rand(1) < new_con_prob and hN1.key != hN2.key:
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
        for hN in self.hidden_Nodes:
            for oN in self.out_Nodes:
                if np.random.rand(1) < new_con_prob:
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
            print(nx.find_cycle(G))
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
        self.bias = np.random.normal(0,1)
    #print the node
    def p_node(self):
        print("Key: " + str(self.key),end=" ")
        print("Type: " + str(self.type),end=" ")
        print("Bias: " + str(self.bias))



#checks if con1 == con2
def same_connection(con1,con2):
        return con1.in_Node.key == con2.in_Node.key and con1.out_Node.key == con2.out_Node.key


#checks if a list contains con
def contains_connection(con,l_cons):
    for c in l_cons:
        if same_connection(c,con):
            return True
        
    return False

#crossover for two genoms
def crossover(genom1,genom2, fit1=None, fit2=None):

        con1 = genom1.connections
        con2 = genom2.connections

        fit1 = fit1 if fit1 is not None else np.random.rand(1)
        fit2 = fit2 if fit2 is not None else np.random.rand(1)

        new_con = []
        for c1 in con1:
            for c2 in con2:
                if same_connection(c1,c2):
                    if c1.is_active == c2.is_active:
                        if np.random.rand(1) < 0.5:
                            new_con.append(c1)
                        else:
                            new_con.append(c2)
                        break
                    elif c1.is_active:
                        if np.random.rand(1) < 0.75:
                            new_con.append(c1)
                        else:
                            new_con.append(c2)
                    else:
                        if np.random.rand(1) < 0.75:
                            new_con.append(c2)
                        else:
                            new_con.append(c1)
        if fit1 >= fit2:
            for c1 in con1:
                if not contains_connection(c1, new_con):
                    new_con.append(c1)
        else:
            for c2 in con2:
                if not contains_connection(c2, new_con):
                    new_con.append(c2)

        g = Genom(2,1)
        g.in_Nodes = genom1.in_Nodes
        g.out_Nodes = genom1.out_Nodes
        hidden_Nodes = []
        hidden_keys = []
        for c in new_con:
            if not c.in_Node.key in hidden_keys and c.in_Node.type == "hidden":
                hidden_keys.append(c.in_Node.key)
                hidden_Nodes.append(Node(c.in_Node.key))
            if not c.out_Node.key in hidden_keys and c.out_Node.type == "hidden":
                hidden_keys.append(c.out_Node.key)
                hidden_Nodes.append(Node(c.out_Node.key))

        g.hidden_Nodes = hidden_Nodes
        g.connections = new_con
        g.n_nodes = len(g.out_Nodes) + len(g.hidden_Nodes)
        #g.visualize()

        return g

#calc distance of two genoms
def distance(genom1 : Genom, genom2 : Genom, c1=1, c3=0.4, N=1):
    avg_weight = 0

    for c in (genom1.connections + genom2.connections):
        avg_weight += c.weight
    avg_weight /= len(genom1.connections + genom2.connections)

    excess = 0
    contains = 0

    for c in genom1.connections:
        if not genom2.has_connection(c):
            excess += 1
        else:
            contains += 1

    excess += len(genom2.connections) -contains
    
    distance = c1*excess/N + c3*avg_weight
    return distance