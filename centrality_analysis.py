import networkx as nx
import pandas as pd


def calculate_centrality(graph, centrality_type):
    switch = {
        "DC": nx.degree_centrality,
        "CC": nx.closeness_centrality,
        "BC": nx.betweenness_centrality
    }

    centrality = switch[centrality_type](graph)
    data_frame = pd.DataFrame.from_dict(centrality, orient="index", columns=[centrality_type])

    data_frame.sort_values(by=centrality_type, ascending=False, inplace=True)
    print(data_frame.head(10))
    print()


def calculate_centralities(graph):
    calculate_centrality(graph, "DC")
    calculate_centrality(graph, "CC")
    calculate_centrality(graph, "BC")


def eigenvector_centrality(graph):
    centrality = nx.eigenvector_centrality(graph, weight="weight")
    data_frame = pd.DataFrame.from_dict(centrality, orient="index", columns=["EVC"])

    data_frame.sort_values(by="EVC", ascending=False, inplace=True)
    print(data_frame.head(10))
    print()


def katz_centrality(graph):
    lambda_max = max(nx.adjacency_spectrum(graph))
    print(f"Alpha < {1 / lambda_max}")


def analyze():
    SNet = nx.read_gml("models/snet.gml")
    SNetF = nx.read_gml("models/snetf.gml")
    SNetT = nx.read_gml("models/snett.gml")
    UserNet = nx.read_gml("models/usernet.gml")

    graphs = [SNet]
    # graphs = [SNet, SNetF, SNetT, UserNet]
    graph_names = ["SNet", "SNetF", "SNetT", "UserNet"]

    for i, graph in enumerate(graphs):
        # calculate_centralities(graph)
        # eigenvector_centrality(graph)
        katz_centrality(graph)


analyze()