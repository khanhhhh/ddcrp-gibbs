from typing import List, Set

import networkx as nx
import numpy as np
import scipy as sp
import scipy.sparse

def comm_to_label(comm: List[Set[int]]) -> np.ndarray:
    num_nodes = sum([len(c) for c in comm])
    label_list = np.empty(shape=(num_nodes,), dtype=np.int)
    for label, c in enumerate(comm):
        for node in c:
            label_list[node] = label
    return label_list


def label_to_comm(label_list: np.ndarray) -> List[Set[int]]:
    communities = {}
    for node, label in enumerate(label_list):
        if label not in communities:
            communities[label] = set()
        communities[label].add(node)
    return list(communities.values())

def subgraph_by_timestamp(mg: nx.MultiGraph, start: int, end: int) -> nx.Graph:
    edges = filter(
        lambda edge: start <= edge[2]["timestamp"] and edge[2]["timestamp"] < end,
        mg.edges(data=True),
    )
    g = nx.Graph()
    for node in mg.nodes():
        g.add_node(node)
    for u, v, data in edges:
        if g.has_edge(u, v):
            g[u][v]["weight"] += data["weight"]
        else:
            g.add_edge(u, v, weight=data["weight"])
    return g

def similarity_matrix(cluster_label_list: np.ndarray) -> np.ndarray:
    num_points = cluster_label_list.shape[1]
    count: np.ndarray = np.zeros((num_points, num_points), dtype=np.int)
    for label_list in cluster_label_list:
        comm = label_to_comm(label_list)
        for c in comm:
            for i in c:
                for j in c:
                    count[i][j] += 1
    count = count / len(cluster_label_list)
    return count

def receptive_field(g: nx.Graph, hop: int=1) -> sp.sparse.coo_matrix:
    a1 = nx.adjacency_matrix(g) + sp.sparse.identity(g.number_of_nodes())
    out = a1
    while hop > 1:
        hop -= 1
        out = out.__matmul__(a1)
    out = sp.sparse.coo_matrix(out)
    out.data = out.data.astype(np.bool)
    return out