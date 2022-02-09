import networkx as nx
import pandas as pd


def calculate_centrality(graph, centrality_type, graph_name):
    switch = {
        "DC": nx.degree_centrality,
        "CC": nx.closeness_centrality,
        "BC": nx.betweenness_centrality
    }

    centrality = switch[centrality_type](graph)
    data_frame = pd.DataFrame.from_dict(centrality, orient="index", columns=[centrality_type])

    data_frame.sort_values(by=centrality_type, ascending=False, inplace=True)
    data_frame = data_frame.head(10)
    data_frame.to_csv(f"result_tables/{graph_name}_{centrality_type}.csv".lower())


def calculate_centralities(graph, graph_name):
    calculate_centrality(graph, "DC", graph_name)
    calculate_centrality(graph, "CC", graph_name)
    calculate_centrality(graph, "BC", graph_name)


def eigenvector_centrality(graph, graph_name):
    centrality = nx.eigenvector_centrality(graph, weight="weight")
    data_frame = pd.DataFrame.from_dict(centrality, orient="index", columns=["EVC"])

    data_frame.sort_values(by="EVC", ascending=False, inplace=True)
    data_frame = data_frame.head(10)
    data_frame.to_csv(f"result_tables/{graph_name}_EVC.csv".lower())


def katz_centrality(graph, graph_name):
    # lambda_max = max(nx.adjacency_spectrum(graph))
    # print(f"alpha < {1 / lambda_max}")

    alpha = 5e-6
    target_subreddit = "reddit.com"

    def katz(beta, file_name):
        centrality = nx.katz_centrality(graph, alpha=alpha, beta=beta, nstart=None, weight="weight")
        data_frame = pd.DataFrame.from_dict(centrality, orient="index", columns=["Katz"])

        data_frame.sort_values(by="Katz", ascending=False, inplace=True)
        data_frame = data_frame.head(10)
        data_frame.to_csv(file_name.lower())

    katz(1.0, f"result_tables/{graph_name}_katz.csv")

    if target_subreddit in graph:
        beta_map = dict([(node, 1e6 if node == target_subreddit else 1.0) for node in graph])

        katz(beta_map, f"result_tables/{graph_name}_katz_modified.csv")


def analyze():
    SNet = nx.read_gml("models/snet.gml")
    SNetF = nx.read_gml("models/snetf.gml")
    SNetT = nx.read_gml("models/snett.gml")
    UserNet = nx.read_gml("models/usernet.gml")

    # graphs = [SNet]
    graphs = [SNet, SNetF, SNetT, UserNet]
    graph_names = ["SNet", "SNetF", "SNetT", "UserNet"]

    for graph, graph_name in zip(graphs, graph_names):
        print(f"Network {graph_name}...")

        # calculate_centralities(graph, graph_name)
        # eigenvector_centrality(graph, graph_name)
        katz_centrality(graph, graph_name)

        print()


analyze()
