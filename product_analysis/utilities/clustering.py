# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise_distances
from sklearn.cluster import KMeans

def cluster_score(data, cluster_assigns):
    """ Evaluate the score of the cluster assignments for n clusters using the
        pairwise distance of each point in the data to it's assigned cluster
        center
    """
    
    total_distance = 0
    for c in np.unique(cluster_assigns):
        distance = pairwise_distances(data[cluster_assigns == c])
        distance = distance.reshape(-1,1)[distance.reshape(-1,1) != 0]
        
        # Check if there is only one data point in the cluster
        if distance.size > 0:
            total_distance += np.mean(distance.reshape(-1,1)[
                distance.reshape(-1,1) != 0])
    
    return total_distance
    
def find_n_clusters(data, n, clustering=KMeans()):
    """ Compute the optimal cluster assignments of the input data for n
        clusters. Compute the same assignments for randomly generated data to
        utilize the Gap Statistic for evaluating n clusters
    """
        
    # Generate Reference Data
    reference = np.random.rand(*data.shape)
    
    # Cluster and score reference
    trial_scores = []
    for _ in range(0, 2):
        clustering.n_clusters = n
        c_assign = clustering.fit_predict(reference)
        trial_scores.append(cluster_score(reference, c_assign))
    ref_score = np.mean(trial_scores)
    
    # Cluster and score data
    clustering.n_clusters = n
    d_assign = clustering.fit_predict(data)
    data_score = cluster_score(data, d_assign)
    
    gap = np.log(ref_score) - np.log(data_score)
    
    return gap, data_score, ref_score, d_assign

def find_optimal_clusters(data, n_clusters, plot=False):
    """ Find the optimal number of cluster assignments to the input data in
        order to minimize the overall pairwise distance of the data to the
        cluster centers relative to a reference set of randomly generated data
    """
    
    data_score = np.array([])
    reference_score = np.array([])
    clusters = np.array([])
    gaps = np.array([])
    assignments = {}
    for cn in range(1, n_clusters + 1):
        
        gap, d_score, r_score, assign = find_n_clusters(data, cn)
        data_score = np.append(data_score, d_score)
        reference_score = np.append(reference_score, r_score)
        gaps = np.append(gaps, gap)
        clusters = np.append(clusters, cn)
        assignments[cn] = assign
    
    best_fit = int(clusters[np.argmax(np.diff(gaps)) - 1])
    data = np.hstack((data, assignments[best_fit].reshape(-1,1)))
    
    if plot:
        
        if len(data.shape) == 2:
            fig, axes = plt.subplots(3,1, figsize=(20,10))
            for cn in range(best_fit):
                axes[0].plot(data[data[:,2] == cn, 0],
                             data[data[:,2] == cn, 1], '.')
                
                axes[1].plot(clusters, gaps, '.-')
                axes[1].set_xlabel('Number of clusters')
                axes[1].set_ylabel('Gap Statistic')
                
                axes[2].plot(clusters[1:], np.diff(gaps), '.-')
                axes[2].set_xlabel('Number of clusters')
                axes[2].set_ylabel('Change in Gap Statistic')
        else:
            fig, axes = plt.subplots(2,1, figsize=(20,10))
            axes[0].plot(clusters, gaps, '.-')
            axes[0].set_xlabel('Number of clusters')
            axes[0].set_ylabel('Gap Statistic')
            
            axes[1].plot(clusters[1:], np.diff(gaps), '.-')
            axes[1].set_xlabel('Number of clusters')
            axes[1].set_ylabel('Change in Gap Statistic')
            
        fig.suptitle('Number of optimal clusters is: ' + str(best_fit))
        
        return best_fit, data[:, -1], fig
    
    return best_fit, data[:, -1]
        
    