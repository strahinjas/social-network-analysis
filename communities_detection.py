import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import chain, combinations
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import SpectralClustering


def create_dendrogram(graph, graph_name):
    communities = list(nx.community.girvan_newman(graph))
    print(communities)

    # building initial dict of node_id to each possible subset:
    node_id = 0
    init_node2community_dict = {node_id: communities[0][0].union(communities[0][1])}
    for comm in communities:
        for subset in list(comm):
            if subset not in init_node2community_dict.values():
                node_id += 1
                init_node2community_dict[node_id] = subset

    # turning this dictionary to the desired format in @mdml's answer
    node_id_to_children = {e: [] for e in init_node2community_dict.keys()}
    for node_id1, node_id2 in combinations(init_node2community_dict.keys(), 2):
        for node_id_parent, group in init_node2community_dict.items():
            if len(init_node2community_dict[node_id1].intersection(init_node2community_dict[node_id2])) == 0 and group == init_node2community_dict[node_id1].union(init_node2community_dict[node_id2]):
                node_id_to_children[node_id_parent].append(node_id1)
                node_id_to_children[node_id_parent].append(node_id2)

    # also recording node_labels dict for the correct label for dendrogram leaves
    node_labels = dict()
    for node_id, group in init_node2community_dict.items():
        if len(group) == 1:
            node_labels[node_id] = list(group)[0]
        else:
            node_labels[node_id] = ''

    # also needing a subset to rank dict to later know within all k-length merges which came first
    subset_rank_dict = dict()
    rank = 0
    for e in communities[::-1]:
        for p in list(e):
            if tuple(p) not in subset_rank_dict:
                subset_rank_dict[tuple(sorted(p))] = rank
                rank += 1
    subset_rank_dict[tuple(sorted(chain.from_iterable(communities[-1])))] = rank

    # my function to get a merge height so that it is unique (probably not that efficient)
    def get_merge_height(sub):
        sub_tuple = tuple(sorted([node_labels[i] for i in sub]))
        n = len(sub_tuple)
        other_same_len_merges = {k: v for k, v in subset_rank_dict.items() if len(k) == n}
        min_rank, max_rank = min(other_same_len_merges.values()), max(other_same_len_merges.values())
        range = (max_rank-min_rank) if max_rank > min_rank else 1
        return float(len(sub)) + 0.8 * (subset_rank_dict[sub_tuple] - min_rank) / range

    graph = nx.DiGraph(node_id_to_children)
    nodes = graph.nodes()
    leaves = set(n for n in nodes if graph.out_degree(n) == 0)
    inner_nodes = [n for n in nodes if graph.out_degree(n) > 0]

    # Compute the size of each subtree
    subtree = dict((n, [n]) for n in leaves)
    for u in inner_nodes:
        children = set()
        node_list = list(node_id_to_children[u])
        while len(node_list) > 0:
            v = node_list.pop(0)
            children.add(v)
            node_list += node_id_to_children[v]
        subtree[u] = sorted(children & leaves)

    inner_nodes.sort(key=lambda n: len(subtree[n]))  # <-- order inner nodes ascending by subtree size, root is last

    # Construct the linkage matrix
    leaves = sorted(leaves)
    index  = dict((tuple([n]), i) for i, n in enumerate(leaves))
    Z = []
    k = len(leaves)
    for i, n in enumerate(inner_nodes):
        children = node_id_to_children[n]
        x = children[0]
        for y in children[1:]:
            z = tuple(sorted(subtree[x] + subtree[y]))
            i, j = index[tuple(sorted(subtree[x]))], index[tuple(sorted(subtree[y]))]
            Z.append([i, j, get_merge_height(subtree[n]), len(z)])  # <-- float is required by the dendrogram function
            index[z] = k
            subtree[z] = list(z)
            x = z
            k += 1

    # dendrogram
    plt.figure()
    dendrogram(Z, labels=[node_labels[node_id] for node_id in leaves])
    plt.savefig(f"figures/dendrogram_{graph_name}.png")


def spectral_clustering(graph, graph_name):
    np.set_printoptions(precision=0, suppress=True)

    for k in range(2, 30):
        clustering = SpectralClustering(n_clusters=k, assign_labels="discretize", affinity="precomputed")\
            .fit(nx.adjacency_matrix(graph))

        colors = clustering.labels_

        color_labels = []
        cluster_sizes = np.zeros(k)

        for color in colors:
            color_labels.append(str(color))
            cluster_sizes[int(color)] += 1

        colored_graph = nx.Graph()
        for color, node in zip(color_labels, graph.nodes()):
            colored_graph.add_node(node, color=color)

        for edge in graph.edges(data=True):
            colored_graph.add_edge(edge[0], edge[1], weight=edge[2]['weight'])

        nx.write_gml(colored_graph, f"models/spectral/{graph_name}/{graph_name}_spectral_{k}.gml".lower())

        print(f"{k:2}-cluster partition: {cluster_sizes}")


def find_brokers(graph, graph_name):
    # broker -> high betweenness centrality + low network constraint
    centrality = nx.betweenness_centrality(graph, weight="weight")

    if graph.number_of_edges() < 100_000:
        constraint = nx.constraint(graph, weight="weight")
    else:
        constraint = dict([(node, 1.0) for node in graph])

    broker_coefficient = dict()

    for node in centrality:
        broker_coefficient[node] = centrality[node] + (1.0 - constraint[node])

    data_frame = pd.DataFrame.from_dict(centrality, orient="index", columns=["Betweenness Centrality"])
    data_frame["Constraint"] = constraint.values()
    data_frame["Broker Coefficient"] = broker_coefficient.values()

    data_frame.sort_values(by="Broker Coefficient", ascending=False, inplace=True)
    data_frame = data_frame.head(10)
    data_frame.to_csv(f"result_tables/{graph_name}_brokers.csv".lower())


def analyze():
    SNet = nx.read_gml("models/snet.gml")
    SNetF = nx.read_gml("models/snetf.gml")
    SNetT = nx.read_gml("models/snett.gml")
    UserNet = nx.read_gml("models/usernet.gml")

    graphs = [SNetT]
    # graphs = [SNet, SNetF, SNetT, UserNet]

    graph_names = ["SNetT"]
    # graph_names = ["SNet", "SNetF", "SNetT", "UserNet"]

    for graph, graph_name in zip(graphs, graph_names):
        print(f"Network {graph_name}...")

        # create_dendrogram(graph, graph_name)
        spectral_clustering(graph, graph_name)
        # find_brokers(graph, graph_name)

        print()


analyze()
