import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


def set_from_column(column, *data_frames):
    result = set()

    for data_frame in data_frames:
        result |= set(data_frame[column].unique())

    return result


def connect_subreddits(graph, *data_frames):
    user_map = {}

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
            if user in user_map.keys():
                if subreddit_to_add not in user_map[user]:
                    connect_nodes(user_map[user], subreddit_to_add)
                    user_map[user].add(subreddit_to_add)
            else:
                user_map[user] = {subreddit_to_add}


def edge_weight_visualization(graph, threshold):
    edge_weight = [int(graph.edges[edge]["weight"]) for edge in graph.edges]

    edge_weight_keys = list(set(edge_weight))
    edge_weight_keys.sort()
    edge_weight_values = list(map(lambda edge: edge_weight.count(edge), edge_weight_keys))

    plt.bar(edge_weight_keys[threshold:], edge_weight_values[threshold:])
    plt.xlabel("Edge Weight")
    plt.ylabel("Edge Count")
    plt.show()


def generate_snet_filtered(graph, threshold):
    filtered_graph = nx.Graph(graph)

    edges_to_remove = [(a, b) for a, b, attrs in filtered_graph.edges(data=True) if attrs["weight"] <= threshold]
    filtered_graph.remove_edges_from(edges_to_remove)

    return filtered_graph


def generate_snet_target(graph, nodes):
    target_graph = nx.Graph()
    target_graph.add_nodes_from([f"\"{node}\"" for node in nodes])

    for a, b, attrs in graph.edges(data=True):
        target_graph.add_edge(a, b, weight=attrs["weight"])

    return target_graph


# noinspection PyBroadException
def connect_users(graph, submissions, comments):
    user_map = {}

    for index, row in comments.iterrows():
        user = row["author"]
        submission_id = row["link_id"][3:]
        parent_id = row["parent_id"][3:]

        try:
            if submission_id == parent_id:
                author = submissions[submissions["submission_id"] == submission_id]["author"].iloc[0]
            else:
                author = comments[comments["comment_id"] == parent_id]["author"].iloc[0]
        except:
            continue

        if user in user_map.keys():
            if parent_id not in user_map[user]:
                user_map[user].add(parent_id)
                if (user, author) in graph.edges:
                    graph.edges[user, author]["weight"] += 1
                else:
                    graph.add_edge(user, author, weight=1)
        else:
            user_map[user] = {parent_id}
            graph.add_edge(user, author, weight=1)


def create_networks():
    submissions = pd.read_pickle("dataset/cleaned/submissions")
    comments = pd.read_pickle("dataset/cleaned/comments")

    users = set_from_column("author", submissions, comments)
    subreddits = set_from_column("subreddit", submissions, comments)

    print(f"Number of users: {len(users)}")
    print(f"Number of subreddits: {len(subreddits)}")

    # SNet
    SNet = nx.Graph()
    SNet.add_nodes_from(subreddits)
    connect_subreddits(SNet, submissions, comments)
    nx.write_gml(SNet, "models/snet.gml")

    # SNetF
    w_threshold = 3
    edge_weight_visualization(SNet, w_threshold)

    SNetF = generate_snet_filtered(SNet, w_threshold)
    nx.write_gml(SNetF, "models/snetf.gml")

    # SNetT
    subreddits_filter = ["reddit.com", "pics", "worldnews", "programming", "math",
                         "business", "politics", "obama", "science", "technology",
                         "WTF", "AskReddit", "netsec", "philosophy", "videos", "offbeat",
                         "funny", "entertainment", "linux", "geek", "gaming", "comics",
                         "gadgets", "nsfw", "news", "environment", "atheism", "canada",
                         "Economics", "scifi", "bestof", "cogsci", "joel", "Health",
                         "guns", "photography", "software", "history", "ideas"]

    SNetT = generate_snet_target(SNet, subreddits_filter)
    nx.write_gml(SNetT, "models/snett.gml")

    # UserNet
    UserNet = nx.DiGraph()
    UserNet.add_nodes_from(users)
    connect_users(UserNet, submissions, comments)
    nx.write_gml(UserNet, "models/usernet.gml")


create_networks()
