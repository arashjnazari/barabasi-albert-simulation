"""Barabasi-Albert network simulation and comparison with NetworkX."""

import csv
import random
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


# Simulation settings
N = 5000                   # Number of nodes
M = 3                      # Links added with each new node
SEED = 42
OUTPUT = Path(__file__).resolve().parent / "output"


def custom_ba(n, m, seed):
    """Generate a BA network with manually coded preferential attachment."""
    rng = random.Random(seed)
    graph = nx.complete_graph(m + 1)

    # Repeating a node once per link makes high-degree nodes more likely.
    pool = []
    for node, degree in graph.degree():
        pool.extend([node] * degree)

    for new_node in range(m + 1, n):
        targets = set()
        while len(targets) < m:
            targets.add(rng.choice(pool))

        for old_node in targets:
            graph.add_edge(new_node, old_node)
            pool.append(old_node)
        pool.extend([new_node] * m)

    return graph


def degree_distribution(graph):
    counts = Counter(degree for _, degree in graph.degree())
    degrees = sorted(counts)
    probabilities = [counts[k] / graph.number_of_nodes() for k in degrees]
    return degrees, probabilities


def main():
    OUTPUT.mkdir(exist_ok=True)

    custom = custom_ba(N, M, SEED)
    reference = nx.barabasi_albert_graph(
        N, M, seed=SEED + 1, initial_graph=nx.complete_graph(M + 1)
    )
    networks = {"Custom": custom, "NetworkX": reference}

    expected_edges = M * N - M * (M + 1) // 2
    for name, graph in networks.items():
        assert graph.number_of_nodes() == N
        assert graph.number_of_edges() == expected_edges
        assert nx.number_of_selfloops(graph) == 0
        assert nx.is_connected(graph)
        print(f"{name}: nodes={N}, edges={graph.number_of_edges()}, "
              f"mean degree={2 * graph.number_of_edges() / N:.4f}, "
              f"max degree={max(dict(graph.degree()).values())}")
    print("Structural checks passed.")

    with (OUTPUT / "degrees.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["model", "node", "degree"])
        for name, graph in networks.items():
            for node, degree in graph.degree():
                writer.writerow([name, node, degree])

    with (OUTPUT / "summary.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["model", "nodes", "edges", "mean_degree", "max_degree"])
        for name, graph in networks.items():
            edges = graph.number_of_edges()
            max_degree = max(dict(graph.degree()).values())
            writer.writerow([name, N, edges, round(2 * edges / N, 4), max_degree])

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    fig2, ax2 = plt.subplots(figsize=(8, 5))

    for name, graph in networks.items():
        k, p = degree_distribution(graph)
        ccdf = [sum(p[i:]) for i in range(len(k))]
        ax1.loglog(k, p, "o", markersize=4, alpha=0.7, label=name)
        ax2.step(k, ccdf, where="post", label=name)

    # Theoretical BA degree distribution for large networks.
    largest_degree = max(degree for graph in networks.values()
                         for _, degree in graph.degree())
    k_theory = list(range(M, largest_degree + 1))
    p_theory = [2 * M * (M + 1) / (k * (k + 1) * (k + 2))
                for k in k_theory]
    ax1.loglog(k_theory, p_theory, "k--", label="BA theory")

    ax1.set(xlabel="Degree (k)", ylabel="P(K = k)",
            title="Barabasi-Albert degree distribution")
    ax2.set(xlabel="Degree (k)", ylabel="P(K >= k)",
            title="Complementary cumulative distribution (CCDF)")
    ax2.set_xscale("log")
    ax2.set_yscale("log")

    for ax in (ax1, ax2):
        ax.grid(alpha=0.3)
        ax.legend()

    fig1.tight_layout()
    fig2.tight_layout()
    fig1.savefig(OUTPUT / "degree_distribution.png", dpi=180)
    fig2.savefig(OUTPUT / "degree_ccdf.png", dpi=180)
    print("Saved plots and CSV files in the output folder.")
    plt.show()


if __name__ == "__main__":
    main()
