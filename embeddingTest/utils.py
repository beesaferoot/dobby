from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm
import json
from json import JSONEncoder

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

# decodedArrays = json.loads(encodedNumpyData)

# finalNumpyArray = numpy.asarray(decodedArrays["array"])

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


def labelIssues(label_embeddings, embeddings, threshold):
    label_size = len(label_embeddings)
    emb_size = len(embeddings)
    tagged_issues = [None]*emb_size
    for i in range(emb_size):
        temp = []
        for label in range(label_size):
            cosine_sim = cosineSimilarities(label_embeddings[label], embeddings[i])
            if cosine_sim >= threshold:
                temp.append((label, cosine_sim))
        if not (temp is []):
            tagged_issues[i] = temp
    return tagged_issues


# this creates/assigns clusters for every embedding
def clusterIssuesInit(embeddings, threshold):
    _array_size = len(embeddings)
    clusters = [0]*_array_size
    cluster_group = []

    for i in range(_array_size):
        temp = i
        for group in cluster_group:
            if group != i:
                cosine_sim = cosineSimilarities(embeddings[i],  embeddings[group])
                # print(cosine_sim)
                if cosine_sim >= threshold:
                    temp = group
                    break
        if temp != i:
            clusters[i] = temp
        else:
            cluster_group.append(i)
            clusters[i] = i

    return clusters, cluster_group



# this only creates/assigns clusters to new embeddings
def clusterIssuesDelta(clusters, cluster_group, new_embeddings, embeddings, threshold):
    _array_size = len(clusters)
    _new_emb_size = len(new_embeddings)
    for i in range(_new_emb_size):
        temp = _array_size + i
        for group in cluster_group:
            cosine_sim = cosineSimilarities(new_embeddings[i],  embeddings[group])
            if cosine_sim >= threshold:
                temp = group
                break
        if temp != _array_size + i:
            clusters.append(temp)
        else:
            cluster_group.append(_array_size + i)
            clusters.append(_array_size + i)
    return clusters, cluster_group



def clusterIssuesWithLabelDelta(label_embeddings, new_embeddings, threshold):
    pass


def dict_to_list(data_dict):
    data_list = []
    for key in data_dict:
        data_list.append(data_dict[key])
    return data_list


def list_to_dict(data_list):
    data_dict = {}
    for i in range(len(data_list)):
        data_dict[i] = data_list[i]
    return data_dict

def add_the_group_column(issues):
    issues["group"] = {}
    size_ = len(issues["id"])
    for i in range(size_):
        issues["group"][i] = None
    return issues


def add_the_labels_column(issues):
    issues["labels"] = {}
    size_ = len(issues["id"])
    for i in range(size_):
        issues["labels"][i] = []
    return issues


# Clean way of getting a Python Dictionary from Serialised JSON
def preprocessSerializedJson(json_file):
    _json_h = open(json_file, "r")
    _json_data = _json_h.read()
    _json_h.close()
    output = {}
    _json_dict = json.loads(_json_data)
    for key in _json_dict:
        output[key] = {}
        for index in _json_dict[key]:
            output[key][int(index)] = _json_dict[key][index]
    return output