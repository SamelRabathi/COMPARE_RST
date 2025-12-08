import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib.projections")

# Load the matrix from the CSV file without column names
matrix = pd.read_csv('Ergebnisse/LP_Verständlichkeit.csv', header=None)

# Ensure it's a square matrix
if matrix.shape[0] != matrix.shape[1]:
    raise ValueError("The matrix must be square (m*m).")

# Assign default indices and column names if missing
matrix.index = range(matrix.shape[0])
matrix.columns = range(matrix.shape[1])

# Create a directed graph from the adjacency matrix
G = nx.from_pandas_adjacency(matrix, create_using=nx.DiGraph)

# Arrange nodes in a hierarchical top-down layout
try:
    hierarchy = list(nx.topological_sort(G))
    pos = {node: (0, -i) for i, node in enumerate(hierarchy)}
except nx.NetworkXUnfeasible:
    print("Graph contains cycles, cannot guarantee strict topological order.")
    pos = nx.spring_layout(G, seed=42)
    pos = {node: (x, -y) for node, (x, y) in pos.items()}

# Reverse y-coordinates to ensure upward direction
pos = {node: (x, -y) for node, (x, y) in pos.items()}

# Function to filter edges and nodes based on a threshold
def plot_filtered_graph(threshold):
    filtered_edges = [(u, v) for u, v, data in G.edges(data=True) if matrix.loc[u, v] >= threshold]
    filtered_nodes = set(u for u, v in filtered_edges).union(v for u, v in filtered_edges)
    
    filtered_G = G.edge_subgraph(filtered_edges).copy()
    
    # Remove isolated nodes
    isolated_nodes = set(filtered_G.nodes) - filtered_nodes
    filtered_G.remove_nodes_from(isolated_nodes)
    
    # Plot the filtered graph
    plt.figure(figsize=(10, 8))
    nx.draw(filtered_G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_color='black', font_weight='bold', edge_color='gray')
    edge_labels = nx.get_edge_attributes(filtered_G, 'weight')
    nx.draw_networkx_edge_labels(filtered_G, pos, edge_labels=edge_labels)
    plt.title(f'Graph with threshold >= {threshold}')
    plt.savefig('graph_plot.png')
    print('Graph saved as graph_plot.png')

# Static plot with user-defined threshold
threshold = 5  # Set your desired threshold here
plot_filtered_graph(threshold)