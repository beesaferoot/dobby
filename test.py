from botbrain import BotBrain
from github import Github, GithubIntegration, Issue, IssueComment, Repository
import json

def get_json_file(file: str):
    hfile = open(file)
    json_data = hfile.read()
    hfile.close()
    return json.loads(json_data)

repo_ = get_json_file("issues_event.json")

def indexify(data_tuple: str):
    size_ = len(data_tuple)
    result = {}
    for i in range(size_):
        result[i] = data_tuple[i]
    return result

if __name__ == "__main__":
    test_ = BotBrain('embed-multilingual-v2.0')
    # print(repo_["payload"]["issue"]["id"])
    issue = repo_["payload"]["issue"]["title"]
    print(test_.label_issues([issue]))