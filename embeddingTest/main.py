from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from utils import  clusterIssuesWithLabelInit, dict_to_list


class IssueClusterer:
    label_embeddings = []
    
    def __init__(self, labels, model):
        self.model = SentenceTransformer(model)
        self.label_embeddings = self.getEmbeddings(dict_to_list(labels["label_description"]))

    def setNewLabelSet(self, labels):
        self.label_embeddings = self.getEmbeddings(dict_to_list(labels["label_description"]))
        pass

    def getEmbeddings(self, sentences):
        return self.model.encode(sentences)


    def cluster(self, github_issues, threshold):
        issue_embeddings = self.getEmbeddings(dict_to_list(github_issues["issue_title"]))
        clusters = clusterIssuesWithLabelInit(self.label_embeddings, issue_embeddings, threshold)
        tagged_issues = {"issue_id": {}, "label_id": {}, "label_tag": {}}
        for i in range(len(github_issues["id"])):
            tagged_issues["issue_id"][i] = github_issues["id"][i]
            if not (clusters[i] is None):
                tagged_issues["label_id"][i] = labels["id"][clusters[i]]
                tagged_issues["label_tag"][i] = labels["label_tag"][clusters[i]]
            else:
                tagged_issues["label_id"][i] = None
                tagged_issues["label_tag"][i] = None
        return tagged_issues

if __name__ == "__main__":
    labels = {
        "id" : {0: 0, 1: 1, 2: 2},
        "label_tag" : {0: "bug", 1: "enhancement", 2: "documentation"},
        "label_description" : 
            {0: "Something isn't working", 1: "New feature or request", 2: "improvements or additions to documentation"}
    }


    github_issues = {
        "id": {0: 0, 1: 1, 2: 2},
        "issue_title" : 
            {0: "No description of the foo function in the documentation",
             1: "Serialize function returns null",
             2: "Add a deserialized function"},
    }
        
    test_ = IssueClusterer(labels=labels, model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')


    print(test_.cluster(github_issues=github_issues, threshold=-1))# -1 implies no threshold