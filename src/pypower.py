import pandapower as pp
import pandapower.networks as nw
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandapower.plotting as plot

# Load a standard power system model from pandapower
net = nw.case33bw()  # This is an example network similar to case33bw in MATPOWER

# Convert the pandapower network to a NetworkX graph
G = pp.topology.create_nxgraph(net)

# Number of nodes to move
num_nodes_to_move = 3

# Ensure there are enough nodes to move
if G.number_of_nodes() <= num_nodes_to_move:
    raise ValueError('Not enough nodes in the graph to move.')

# Function to check if moving a node will split the graph
def is_critical_node(G, node):
    G_copy = G.copy()
    G_copy.remove_node(node)
    return not nx.is_connected(G_copy)

# Select three random nodes (without replacement), avoiding critical nodes
all_nodes = list(G.nodes)
non_critical_nodes = [node for node in all_nodes if not is_critical_node(G, node)]
if len(non_critical_nodes) < num_nodes_to_move:
    raise ValueError('Not enough non-critical nodes to move.')
nodes_to_move = np.random.choice(non_critical_nodes, num_nodes_to_move, replace=False)

# Function to move nodes and maintain radialness
def move_nodes_maintain_radial(G, nodes_to_move):
    for node in nodes_to_move:
        # Disconnect the node by removing all its edges
        original_neighbors = list(G.neighbors(node))
        G.remove_node(node)

        # Attempt to reconnect the node
        for attempt in range(5):  # Allow multiple attempts to reconnect
            possible_nodes = [n for n in G.nodes() if n != node]
            np.random.shuffle(possible_nodes)
            G.add_node(node)
            for new_neighbor in possible_nodes[:2]:  # Try connecting to two nodes
                G.add_edge(node, new_neighbor)
                if nx.is_connected(G):
                    break
                G.remove_edge(node, new_neighbor)
            if nx.is_connected(G):
                break
            G.remove_node(node)  # Remove the node if unable to connect successfully

        if not nx.is_connected(G):
            # If unable to reconnect, restore original edges and move to next node
            G.add_node(node)
            for neighbor in original_neighbors:
                G.add_edge(node, neighbor)
            raise ValueError(f"Failed to maintain connectivity after moving node {node}")

    return G

# Move nodes and maintain radialness
try:
    G = move_nodes_maintain_radial(G, nodes_to_move)
except ValueError as e:
    print(e)

# Plot the updated graph
pos = nx.spring_layout(G)  # positions for all nodes
nx.draw_networkx(G, pos, with_labels=True, node_color='skyblue', node_size=500, font_size=8, font_color='darkred')
plt.title(f'Graph after Attempted Movement of Nodes {nodes_to_move}')
plt.show()


# Assuming generators are at substations, we need to add cost functions to the external grid
# Typically, the external grid is at bus 0 in this case
# Adding a cost function for the external grid
# pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw=100)  # cost in €/MW

# Setting up and running OPF
try:
    pp.runopp(net, verbose=True)  # Run the optimal power flow
    print("OPF successfully executed!")
except Exception as e:
    print("Failed to execute OPF:", e)

# Displaying results

print(net.res_bus)
# Save bus voltages to CSV
net.res_bus.to_csv('voltage_results.csv', index=True)
print("Bus voltages saved to 'voltage_results.csv'.")

# Save line loadings to CSV
net.res_line.to_csv('line_loading_results.csv', index=True)
print("Line loadings saved to 'line_loading_results.csv'.")
