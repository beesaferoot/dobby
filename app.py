import enum
import os

from dotenv import load_dotenv
from flask import Flask, request
from github import Github, GithubIntegration, Issue, IssueComment, Repository
from botbrain import BotBrain

load_dotenv()
app = Flask(__name__)
# app id
app_id = os.getenv('APP_ID')
# Read the bot certificate
with open(
        os.getenv('PATH_TO_CERT'),
        'r'
) as cert_file:
    app_key = cert_file.read()

# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)

botbrain_obj = BotBrain('embed-multilingual-v2.0')

class BotAction(enum.Enum):
    translate = 1
    auto_label = 2

def indexify(data_tuple_list: list):
    size_ = len(data_tuple_list)
    result = []
    for i in range(size_):
        result[i] = data_tuple_list[i]
    return result


@app.route("/", methods=['POST'])
def bot():
    payload = request.json

    if "comment" in payload.keys() and payload["action"] == "created":
        bot_action = BotAction.translate
    elif "issue" in payload.keys() and payload["action"] == "opened":
        bot_action = BotAction.auto_label
    else:
        return "no_op"

    owner = payload['repository']['owner']['login']
    repo_name = payload['repository']['name']

    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id
        ).token
    )
    repo = git_connection.get_repo(f"{owner}/{repo_name}")

    if bot_action == BotAction.auto_label:
        issue_number = payload['issue']['number']
        issue = repo.get_issue(number=issue_number)
        auto_label(repo=repo, issue=issue)
        
        # print(f"{issue.title}")
        
        output = indexify([(issue_number, issue.title)]) #give each issue index
        result = botbrain_obj.label_issues([issue.title]) #returns a list of tuple of issue title with there labels
        final_result = [(output[i][0], result[i][0], result[i][1]) for i in range(len(output))] #retunrs a list of tuple of issue number, title and predicted labels
        print(final_result)
        return 
    if bot_action == BotAction.translate:
        issue_number = payload['issue']['number']
        comment_id = payload['comment']['id']
        comment_body = payload['comment']['body']
        if "@dobby" not in comment_body:
            return
        issue = repo.get_issue(number=issue_number)
        comment = issue.get_comment(comment_id)
        translate_issue_boby(repo, comment)
        return


def auto_label(repo: Repository, issue: Issue):
    pass


def translate_issue_boby(repo: Repository, comment: IssueComment):
    pass


if __name__ == "__main__":
    app.run(debug=True, port=5000)
