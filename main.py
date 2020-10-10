
import networkx as nx
import numpy as np

from src.draw import draw_size, draw_mat
from graph.sbm import sbm, preferential_attachment_cluster
from src.logger import log
from src.model.model import Model
from src.util import comm_to_label, similarity_matrix

seed = 1234
np.random.seed(seed)

# graph
num_clusters = 50
gamma = 2.5
approx_avg_degree = 50
# model
dim = 50

for approx_num_nodes in range(500, 2001, 500):
    g, actual_comm = sbm(preferential_attachment_cluster(num_clusters, gamma), approx_num_nodes, approx_avg_degree)
    log.write_log(f"generated graph: size {g.number_of_nodes()}, cluster size {len(actual_comm)} average degree: {2 * g.number_of_edges() / g.number_of_nodes()} max modularity: {nx.algorithms.community.quality.modularity(g, actual_comm)}")
    draw_size([len(c) for c in actual_comm], name="actual_size", log=True)

    upper_scale = 100000
    scale = upper_scale
    while True:
        log.write_log(f"scale {scale}")
        model = Model(seed, g.number_of_nodes(), dim)
        comm, kmeans_improved_comm, kmeans_comm = model.iterate(g, ddcrp_scale=scale)
        diff = abs(len(kmeans_improved_comm) - len(actual_comm)) / len(actual_comm)
        log.write_log(f"scale {scale} diff {diff}")
        log.write_log(f"cluster size {len(kmeans_improved_comm)} kmeans improved modularity: {nx.algorithms.community.quality.modularity(g, kmeans_improved_comm)}")
        log.write_log(f"cluster size {len(kmeans_comm)} kmeans naive    modularity: {nx.algorithms.community.quality.modularity(g, kmeans_comm)}")
        if diff < 0.1:
            break
        if len(kmeans_improved_comm) > len(actual_comm):
            upper_scale = scale
            scale /= 2
        else:
            scale = (upper_scale + scale) / 2
