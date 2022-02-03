import networkx as nx
import matplotlib.pyplot as plt


SNet = nx.read_gml("models/snet.gml")
SNetF = nx.read_gml("models/snetf.gml")
SNetT = nx.read_gml("models/snett.gml")
UserNet = nx.read_gml("models/usernet.gml")


def clustering_coef_distribution(graph, graph_name, weight):
    print("Using edges weight..." if weight else "Without edges weight...")

    avg_clustering_coef = nx.average_clustering(graph, weight=weight)
    all_clustering_coef = [coef for coef in nx.clustering(graph, weight=weight).values() if coef > 0]
    global_clustering_coef = max(all_clustering_coef)
    print("\tAverage clustering coefficient:", avg_clustering_coef)
    print("\tGlobal clustering coefficient: ", global_clustering_coef)

    plt.hist(all_clustering_coef, bins=50)
    plt.gca().set(title=f"{graph_name}", ylabel="Count", xlabel="Clustering Coefficient")
    plt.savefig((f"figures/{graph_name}_cc_dist_" + ("weight" if weight else "no_weight") + ".png").lower())
    plt.clf()


def clustering_coef_calculation(graphs, graph_names, weights):
    for i, graph in enumerate(graphs):
        print(f"Network {graph_names[i]}:")
        node_num = graph.number_of_nodes()
        edge_num = graph.number_of_edges()
        random_network = nx.erdos_renyi_graph(node_num, (2*edge_num)/((node_num-1)*node_num))

        for weight in weights:
            clustering_coef_distribution(graph, graph_names[i], weight)
            clustering_coef_distribution(random_network, f"random_{graph_names[i]}", weight)


clustering_coef_calculation([SNet, SNetF, SNetT, UserNet], ["SNet", "SNetF", "SNetT", "UserNet"], [None, "weight"])
