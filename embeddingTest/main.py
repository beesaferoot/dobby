from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import json
from utils import  (
    clusterIssuesWithLabelInit, 
    dict_to_list, 
    add_the_labels_column, 
    add_the_group_column,
    clusterIssuesInit,
    list_to_dict,
    NumpyArrayEncoder,
    preprocessSerializedJson,
    labelIssues
    )



class IssueClusterer:
    label_embeddings = []
    
    def __init__(self, model):
        self.model = SentenceTransformer(model)
        # self.label_embeddings = self.getEmbeddings(dict_to_list(labels["label_description"]))

    def setNewLabelSet(self, labels):
        self.label_embeddings = self.getEmbeddings(dict_to_list(labels["label_description"]))


    def getEmbeddings(self):
        embedding_json = open("data/embeddings.json", "r")
        embedding_json_data = embedding_json.read()
        embedding_dict = json.loads(embedding_json_data)
        embedding_list = dict_to_list(embedding_dict["issue_embeddings"])
        return np.asarray(embedding_list)  


    def createEmbeddings(self, github_issues):
        issue_embeddings = self.model.encode(dict_to_list(github_issues["issue_title"]))
        github_issues["issue_embeddings"] = {}
        for i in range(len(github_issues["id"])):
            github_issues["issue_embeddings"][i] = issue_embeddings[i]
        embeddings_json = open("data/embeddings.json", "w")
        embeddings_json.write(json.dumps(github_issues, cls=NumpyArrayEncoder))
        embeddings_json.close()


    #to-do Catch error if file is not create or file is empty
    def insertNewEmbeddings(self, new_github_issues):
        new_github_embeddings =\
            self.model.encode(dict_to_list(new_github_issues["issue_title"]))
        _github_issues =\
            preprocessSerializedJson("data/embeddings.json")
        current_size = len(_github_issues["id"])
        
        for i in range(len(new_github_issues["id"])):
            _github_issues["issue_embeddings"][current_size + i] =\
                new_github_embeddings[i]
            _github_issues["id"][current_size + i] =\
                new_github_issues["id"][i]
            _github_issues["issue_title"][current_size + i] =\
                new_github_issues["issue_title"][i]
        embeddings_json = open("data/embeddings.json", "w+")
        embeddings_json.write(json.dumps(_github_issues, cls=NumpyArrayEncoder))
        embeddings_json.close()
           

    def cluster(self, threshold):
        issue_embeddings = self.getEmbeddings()
        (clusters, _) = clusterIssuesInit(issue_embeddings, threshold)
        grouped_issues = {"issue_id" : {}, "group_id" : {}}
        _github_issues = preprocessSerializedJson("data/embeddings.json")
        for i in range(len(_github_issues["id"])):
            grouped_issues["issue_id"][i] = _github_issues["id"][i]
            if not(clusters[i] is None):
                grouped_issues["group_id"][i] = _github_issues["id"][clusters[i]]
            else:
                grouped_issues["group_id"][i] = None
        cluster_json = open("data/cluster.json", "w+")
        cluster_json.write(json.dumps(grouped_issues))
        cluster_json.close()

    
    def tagIssues(self, labels, threshold):
        _label_embeddings =\
            self.model.encode(dict_to_list(labels["label_description"]))
        issue_embeddings = self.getEmbeddings()
        issueAndTags = labelIssues(_label_embeddings, issue_embeddings, threshold=threshold)
        # print(issueAndTags)
        _github_issues = preprocessSerializedJson("data/embeddings.json")
        tagged_issues = {"issue_id": {}, "label_id": {}, "label_tag": {}}
        for i in range(len(_github_issues["id"])):
            tagged_issues["issue_id"][i] = _github_issues["id"][i]
            if not (issueAndTags[i] == []):
                tagged_issues["label_id"][i] = issueAndTags[i]
                # tagged_issues["label_tag"][i] = labels["label_tag"][issueAndTags[i]]
            else:
                tagged_issues["label_id"][i] = None
                # tagged_issues["label_tag"][i] = None
        cluster_json = open("data/tagged_issues.json", "w+")
        cluster_json.write(json.dumps(tagged_issues))
        cluster_json.close()
        


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
             1: "Serialze function returns null",
             2: "Add a deserialized function"},
    }

    new_github_issues = {
        "id": {0: 3},
        "issue_title" : 
            {0: "No description of the foo function in the documentation"},
    }
     
        
    test_ = IssueClusterer(model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
    
    # creates the seed embeddings 
    # test_.createEmbeddings(github_issues=github_issues)

    # test_.cluster(threshold=0.5)

    # test_.insertNewEmbeddings(new_github_issues=new_github_issues)
    # print(test_.cluster(github_issues=github_issues, threshold=0.5))# -1 implies no threshold

    # print(add_the_labels_column(github_issues))

    # test_.cluster(threshold=0.5)
    # test_.tagIssues(labels, threshold=0.4)



    

