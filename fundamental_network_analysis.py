from collections import Counter

import networkx as nx
import matplotlib.pyplot as plt
import powerlaw
from numpy import NaN


def clustering_coefficient_distribution(graph, graph_name, weight):
    print("Using edges weight..." if weight else "Without edges weight...")

    average_clustering = nx.average_clustering(graph, weight=weight)
    clustering_coefficients = [coefficient for coefficient in nx.clustering(graph, weight=weight).values()
                               if coefficient > 0]
    global_clustering = max(clustering_coefficients)

    print("\tAverage clustering coefficient:", average_clustering)
    print("\tGlobal clustering coefficient: ", global_clustering)

    plt.hist(clustering_coefficients, bins=50)
    plt.gca().set(title=f"{graph_name}", xlabel="Clustering Coefficient", ylabel="Count")
    plt.savefig((f"figures/{graph_name}_cc_dist_" + ("weight" if weight else "no_weight") + ".png").lower())
    plt.clf()


def clustering_coefficient_calculation(graph, graph_name, weights):
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    random_network = nx.erdos_renyi_graph(node_count, (2 * edge_count) / ((node_count - 1) * node_count))

    for weight in weights:
        clustering_coefficient_distribution(graph, graph_name, weight)
        clustering_coefficient_distribution(random_network, f"random_{graph_name}", weight)


def small_world(graph):
    if not graph.is_directed():
        sigma = nx.sigma(graph)
        omega = nx.omega(graph)

        print(f"Small-world coefficient sigma: {sigma}")
        print("A graph is commonly classified as small-world if sigma > 1")
        print()
        print(f"Small-world coefficient omega: {omega}")
        print("omega =  0 -> graph has small-world characteristics")
        print("omega = -1 -> graph has a lattice shape")
        print("omega =  1 -> random graph")


def assortativity_analysis(graph):
    if graph.is_directed():
        dac_in = nx.degree_assortativity_coefficient(graph, x="out", y="in")
        dac_in_weighted = nx.degree_assortativity_coefficient(graph, x="out", y="in", weight="weight")

        print(f"In-degree assortativity coefficient: {dac_in:.5f}")
        print(f"Weighted in-degree assortativity coefficient: {dac_in_weighted:.5f}")

        dac_out = nx.degree_assortativity_coefficient(graph, x="in", y="out")
        dac_out_weighted = nx.degree_assortativity_coefficient(graph, x="in", y="out", weight="weight")

        print(f"Out-degree assortativity coefficient: {dac_out:.5f}")
        print(f"Weighted out-degree assortativity coefficient: {dac_out_weighted:.5f}")
    else:
        dac = nx.degree_assortativity_coefficient(graph)
        dac_weighted = nx.degree_assortativity_coefficient(graph, weight="weight")

        print(f"Degree assortativity coefficient: {dac:.5f}")
        print(f"Weighted degree assortativity coefficient: {dac_weighted:.5f}")


def rich_club(graph, graph_name):
    if not graph.is_directed():
        rc = nx.rich_club_coefficient(graph, normalized=False, seed=42)

        x, y = zip(*rc.items())

        plt.plot(x, y)
        plt.gca().set(title=f"{graph_name}", xlabel="Degree", ylabel="Rich Club Coefficient")
        plt.savefig(f"figures/{graph_name}_rich_club.png".lower())
        plt.clf()


def degree_distribution(graph, graph_name):
    degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
    degree_count = Counter(degree_sequence)

    x, y = zip(*degree_count.items())

    plt.scatter(x, y, marker=".")
    plt.gca().set(title=f"{graph_name} Degree Distribution",
                  xlabel="Degree", xscale="linear", xlim=(1, max(x)),
                  ylabel="Count", yscale="linear", ylim=(1, max(y)))
    plt.savefig(f"figures/{graph_name}_degree_distribution.png".lower())
    plt.clf()

    results = powerlaw.Fit(degree_sequence)

    if results.power_law.xmin is NaN:
        return

    print(results.power_law.alpha)
    print(results.power_law.xmin)
    print(results.power_law.sigma)

    R, p = results.distribution_compare("power_law", "exponential")
    print(f"Loglikelihood ratio: {R}")
    print(f"Statistical significance: {p}")

    R, p = results.distribution_compare("power_law", "truncated_power_law")
    print(f"Loglikelihood ratio: {R}")
    print(f"Statistical significance: {p}")


def analyze():
    SNet = nx.read_gml("models/snet.gml")
    SNetF = nx.read_gml("models/snetf.gml")
    SNetT = nx.read_gml("models/snett.gml")
    UserNet = nx.read_gml("models/usernet.gml")

    # graphs = [SNetT]
    graphs = [SNet, SNetF, SNetT, UserNet]
    graph_names = ["SNet", "SNetF", "SNetT", "UserNet"]

    for graph, graph_name in zip(graphs, graph_names):
        print(f"Network {graph_name}...")

        clustering_coefficient_calculation(graph, graph_name, [None, "weight"])
        # small_world(graph)
        assortativity_analysis(graph)
        rich_club(graph, graph_name)
        degree_distribution(graph, graph_name)

        print()


analyze()
