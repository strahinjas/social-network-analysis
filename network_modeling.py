import networkx as nx
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

            if user in result.keys() and subreddit_to_add not in result[user]:
                connect_nodes(result[user], subreddit_to_add)
                result[user].add(subreddit_to_add)
            else:
                result[user] = {subreddit_to_add}

    return result


submissions = pd.read_pickle("dataset/cleaned/submissions")
comments = pd.read_pickle("dataset/cleaned/comments")

users = set_from_column("author", submissions, comments)
subreddits = set_from_column("subreddit", submissions, comments)

SNet = nx.Graph()
SNet.add_nodes_from(subreddits)

subreddit_user_map = subreddits_per_user(SNet, submissions, comments)

nx.write_pajek(SNet, "models/snet.net")
