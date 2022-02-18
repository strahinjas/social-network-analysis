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
    result = data_frame

    data_frame.sort_values(by=centrality_type, ascending=False, inplace=True)
    data_frame = data_frame.head(10)
    data_frame.to_csv(f"result_tables/{graph_name}_{centrality_type}.csv".lower())

    return result


def calculate_centralities(graph, graph_name):
    df_dc = calculate_centrality(graph, "DC", graph_name)
    df_cc = calculate_centrality(graph, "CC", graph_name)
    df_bc = calculate_centrality(graph, "BC", graph_name)

    return pd.concat([df_dc, df_cc, df_bc], axis=1)


def eigenvector_centrality(graph, graph_name):
    centrality = nx.eigenvector_centrality(graph, weight="weight")
    data_frame = pd.DataFrame.from_dict(centrality, orient="index", columns=["EVC"])
    result = data_frame

    data_frame.sort_values(by="EVC", ascending=False, inplace=True)
    data_frame = data_frame.head(10)
    data_frame.to_csv(f"result_tables/{graph_name}_EVC.csv".lower())

    return result


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


def composite_centrality(graph, graph_name, centralities):
    columns = ["DC", "CC", "BC", "EVC"]

    for column in columns:
        centralities[f"{column}_RANK"] = centralities[column].rank(ascending=False)

    centralities["COMPOSITE_RANK"] = centralities["DC_RANK"] * centralities["CC_RANK"] * \
                                     centralities["BC_RANK"] * centralities["EVC_RANK"]

    centralities.sort_values(by="COMPOSITE_RANK", ascending=True, inplace=True)
    centralities = centralities.head(10)
    centralities.to_csv(f"result_tables/{graph_name}_composite.csv".lower())


def analyze():
    SNet = nx.read_gml("models/snet.gml")
    SNetF = nx.read_gml("models/snetf.gml")
    SNetT = nx.read_gml("models/snett.gml")
    UserNet = nx.read_gml("models/usernet.gml")

    # graphs = [SNet]
    graphs = [SNet, SNetF, SNetT, UserNet]

    # graph_names = ["SNet"]
    graph_names = ["SNet", "SNetF", "SNetT", "UserNet"]

    for graph, graph_name in zip(graphs, graph_names):
        print(f"Network {graph_name}...")

        centralities = calculate_centralities(graph, graph_name)
        df_evc = eigenvector_centrality(graph, graph_name)
        centralities = pd.concat([centralities, df_evc], axis=1)

        katz_centrality(graph, graph_name)
        composite_centrality(graph, graph_name, centralities)

        print()


analyze()
