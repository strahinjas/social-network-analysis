# !import networkx as nx
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


def set_from_column(column, *data_frames):
    result = set()

    for data_frame in data_frames:
        result |= set(data_frame[column].unique())

    return result


def subreddits_per_user(graph, *data_frames):
    result = {}

    def connect_nodes(subreddit_set, new_subreddit):
        for subreddit in subreddit_set:
            if (subreddit, new_subreddit) in graph.edges:
                graph.edges[subreddit, new_subreddit]["weight"] += 1
            else:
                graph.add_edge(subreddit, new_subreddit, weight=1)

    for data_frame in data_frames:
        for _, row in data_frame.iterrows():
            user = row["author"]
            subreddit_to_add = row["subreddit"]

            # fixed (?)
            if user in result.keys():
                if subreddit_to_add not in result[user]:
                    connect_nodes(result[user], subreddit_to_add)
                    result[user].add(subreddit_to_add)
            else:
                result[user] = {subreddit_to_add}

    return result


def edge_weight_visualization(graph, threshold):
    edge_weight = [int(graph.edges[edge]['weight']) for edge in graph.edges]

    edge_weight_keys = list(set(edge_weight))
    edge_weight_keys.sort()
    edge_weight_values = list(map(lambda edge: edge_weight.count(edge), edge_weight_keys))

    plt.bar(edge_weight_keys[threshold:], edge_weight_values[threshold:])
    plt.xlabel('Edge Weight')
    plt.ylabel('Edge Num')
    plt.show()


def generate_snet_filtered(graph, threshold):
    to_remove = [(a, b) for a, b, attrs in graph.edges(data=True) if attrs['weight'] <= threshold]
    graph.remove_edges_from(to_remove)
    return graph


def generate_snet_target(graph, nodes):
    nodes_to_remove = [node for node in graph.nodes if node not in nodes]
    graph.remove_nodes_from(nodes_to_remove)
    new_graph = nx.Graph()
    new_graph.add_nodes_from(nodes)
    for a, b, attrs in graph.edges(data=True):
        new_graph.add_edge(a, b, weight=attrs['weight'])
    return new_graph


def create_networks():
    submissions = pd.read_pickle("dataset/cleaned/submissions")
    comments = pd.read_pickle("dataset/cleaned/comments")

    users = set_from_column("author", submissions, comments)
    subreddits = set_from_column("subreddit", submissions, comments)

    # SNet
    SNet = nx.Graph()
    SNet.add_nodes_from(subreddits)
    subreddit_user_map = subreddits_per_user(SNet, submissions, comments)
    nx.write_pajek(SNet, "models/snet.net")

    # SNet = nx.Graph(nx.read_pajek("dataset/models/snet.net"))

    # SNetF
    w_threshold = 3
    edge_weight_visualization(SNet, w_threshold)

    SNetF = generate_snet_filtered(SNet, w_threshold)
    nx.write_pajek(SNetF, "models/snetf.net")

    # SNetT
    subreddits_filter = ['reddit.com', 'pics', 'worldnews', 'programming', 'math',
                        'business', 'politics', 'obama', 'science', 'technology',
                        'WTF', 'AskReddit', 'netsec', 'philosophy', 'videos', 'offbeat',
                        'funny', 'entertainment', 'linux', 'geek', 'gaming', 'comics',
                        'gadgets', 'nsfw', 'news', 'environment', 'atheism', 'canada',
                        'Economics', 'scifi', 'bestof', 'cogsci', 'joel', 'Health',
                        'guns', 'photography', 'software', 'history', 'ideas']

    SNetT = generate_snet_target(SNet, subreddits_filter)
    nx.write_pajek(SNetT, "models/snett.net")


create_networks()
