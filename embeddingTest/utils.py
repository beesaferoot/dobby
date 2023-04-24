from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm


def cosineSimilarities(A,  B):
    return np.dot(A,B)/(norm(A)*norm(B))


def clusterIssuesWithLabelInit(label_embeddings, embeddings, threshold):
    label_size = len(label_embeddings)
    emb_size = len(embeddings)
    clusters = [None]*emb_size
    for i in range(emb_size):
        temp = (None, None)
        for label in range(label_size):
            cosine_sim = cosineSimilarities(label_embeddings[label], embeddings[i])
            if temp[0] is None:
                if cosine_sim >= threshold:
                    temp = (label, cosine_sim)
            else:
                if (cosine_sim >= threshold) and (cosine_sim > temp[1]):
                        temp = (label, cosine_sim)
        if not (temp[0] is None):
            clusters[i] = temp[0]
    return clusters


def clusterIssuesWithLabelDelta(label_embeddings, new_embeddings, threshold):
    pass


def dict_to_list(data_dict):
    data_list = []
    for key in data_dict:
        data_list.append(data_dict[key])
    return data_list



