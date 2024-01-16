import numpy as np
from numpy import genfromtxt
import networkx as nx
import matplotlib.pyplot as plt
import numpy.linalg as LA


def matrix_load(file):
    my_data = genfromtxt(file, delimiter=',')
    my_data = my_data.astype(int)
    if my_data.shape[1] == 3: my_data = np.delete(my_data, 2, axis=1)
    if np.amin(my_data) == 1: my_data -= 1
    n = np.amax(my_data) + 1 
    matrix = np.zeros((n,n))
    G = nx.Graph()
    for e in my_data:
        matrix[e[0]][e[1]] = 1
        G.add_edge(e[0], e[1])
    return matrix, G

m_e, graph_e = matrix_load('./data/my_example.dat')
m1, graph1 = matrix_load('./data/example1.dat')
m2, graph2 = matrix_load('./data/example2.dat')





def load_node_colors(file):
    colors = {1: 'blue', 2: 'purple', 3: 'yellow', 4: 'red'}
    r = []
    with open(file, 'r') as f:
        c = f.readlines()
        c = [int(x.strip()) for x in c]
        r = [colors[x] for x in c]
    return r

graph1_node_clusters = load_node_colors('./data/nodes_by_cluster1.txt')
graph2_node_clusters = load_node_colors('./data/nodes_by_cluster2.txt')

print(f'len g1: {graph1.number_of_nodes()} len g1 colors: {len(graph1_node_clusters)}')
print(f'len g2: {graph2.number_of_nodes()} len g2 colors: {len(graph2_node_clusters)}')

nx.draw_networkx(graph_e, node_size=200, width=1)
plt.savefig("plot1.png", dpi=1000)
plt.show()
nx.draw(graph1, node_size=10, nodelist=[i for i in range(len(graph1_node_clusters))], node_color=graph1_node_clusters, width=0.2)
plt.savefig("plot2.png", dpi=1000)
plt.show()
nx.draw(graph2, node_size=20, nodelist=[i for i in range(len(graph2_node_clusters))], node_color=graph2_node_clusters, width=0.2)
plt.savefig("plot3.png", dpi=1000)
plt.show()

# nx.draw(graph1, node_size=10, width=0.2)
# plt.savefig("plot2.png", dpi=1000)
# plt.show()
# nx.draw(graph2, node_size=20, width=0.2)
# plt.savefig("plot3.png", dpi=1000)
# plt.show()






