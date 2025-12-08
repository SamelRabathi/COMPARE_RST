import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

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

# Separate connected components to prevent overlap
subgraphs = [G.subgraph(c).copy() for c in nx.weakly_connected_components(G)]

# Function to process each subgraph layout
def process_subgraph(args):
    idx, subgraph, x_offset, y_offset = args
    try:
        hierarchy = list(nx.topological_sort(subgraph))
        sub_pos = {node: (x_offset + i * 2, y_offset - idx * 5) for i, node in enumerate(hierarchy)}
        return sub_pos, len(hierarchy)
    except nx.NetworkXUnfeasible:
        sub_pos = nx.spring_layout(subgraph, seed=42, k=0.8)
        sub_pos = {node: (x_offset + x, y_offset - idx * 5 - y) for node, (x, y) in sub_pos.items()}
        return sub_pos, len(sub_pos)

# Use multiprocessing to calculate positions
pos = {}
x_offset = 0
y_offset = 0
args = [(idx, subgraph, x_offset + idx * 10, y_offset) for idx, subgraph in enumerate(subgraphs)]

with Pool(cpu_count()) as pool:
    results = pool.map(process_subgraph, args)

for sub_pos, length in results:
    pos.update(sub_pos)
    x_offset += length * 3
    y_offset -= 10

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
    plt.figure(figsize=(16, 12))
    nx.draw(filtered_G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_color='black', font_weight='bold', edge_color='gray')
    edge_labels = nx.get_edge_attributes(filtered_G, 'weight')
    nx.draw_networkx_edge_labels(filtered_G, pos, edge_labels=edge_labels)
    plt.title(f'Graph with threshold >= {threshold}')
    plt.savefig('graph_plot.png')
    print('Graph saved as graph_plot.png')

# Static plot with user-defined threshold
threshold = 2  # Set your desired threshold here
plot_filtered_graph(threshold)
