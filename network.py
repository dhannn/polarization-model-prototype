import networkx as nx
import matplotlib.pyplot as plt
import random
graph1 = nx.powerlaw_cluster_graph(100, int(500 * .01), 0.5)
graph2 = nx.powerlaw_cluster_graph(100, int(500 * .01), 0.5)

combined_graph1 = nx.union(graph1, graph2, ('g1-', 'g2'))

_graph1 = nx.relabel_nodes(graph1, { n: str(n) if n==0 else 'a-'+str(n) for n in  graph1.nodes })
_graph2 = nx.relabel_nodes(graph2, { n: str(n) if n==0 else 'b-'+str(n) for n in  graph2.nodes })
combined_graph2 = nx.compose(_graph1, _graph2)

# print(graph.edges())

# graph.remove_edges_from(list(nx.selfloop_edges(graph)))

# for u, v in graph.edges():
#     for w in graph[u][v]:
#         graph[u][v][w]['weight'] = random.random()
#         # print(graph[u][v][w])

#     # print(f'[{u}, {v}]', end='\t')

# for u, v in graph.edges():
#     for w in graph[u][v]:
#         print(f'({u}, {v}, {w})\t{graph.get_edge_data(u, v, w)}')

# with open('edgelist2', 'w') as edgelist:
nx.edgelist.write_edgelist(combined_graph2, 'edgelist5.csv')

fig, ax = plt.subplots()
# nx.draw_spring(graph, ax=ax)
# pos = nx.bipartite_layout(graph, graph.nodes)
# pos = nx.circular_layout(graph) 
# pos = nx.shell_layout(graph, scale=10)
nx.draw_circular(graph, ax=ax, with_labels=False, node_size=100, arrowsize=5)
# nx.draw_networkx(graph, pos=pos, ax=ax, node_size=100, with_labels=False)
# nx.draw_circular(graph,ax=ax, node_size=100, with_labels=False)
fig.set_figheight(15)
fig.set_figwidth(15)
fig.show()
plt.show()
