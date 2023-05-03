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
        auto_label(repo=repo, target_issue=issue)
        return "no_op"
    if bot_action == BotAction.translate:
        issue_number = payload['issue']['number']
        comment_id = payload['comment']['id']
        comment_body = payload['comment']['body']
        if "@dobby" not in comment_body:
            return "no_op"
        issue = repo.get_issue(number=issue_number)
        comment = issue.get_comment(comment_id)
        translate_issue_boby(repo, comment, issue)
        return "no_op"


def auto_label(repo: Repository, target_issue: Issue):
    # dumb approach to fetching issues
    issue_samples = []
    for i, issue in enumerate(repo.get_issues()):
        # only take 90 samples
        if i < 90:
            title, body, labels = issue.title, issue.body, issue.labels
            for label in labels:
                issue_sample = (f"{title} : {body}", label)
                issue_samples.append(issue_sample)
        else:
            break

    bot_brain = BotBrain('embed-multilingual-v2.0')
    predict_label = bot_brain.predict_label_from_issues(issue=f"{target_issue.title} : {target_issue.body}",
                                                        issue_samples=issue_samples)
    if predict_label:
        # auto label issue
        target_issue.set_labels([predict_label])


def translate_issue_boby(repo: Repository, comment: IssueComment, issue: Issue):
    lang = parse_translate_command_langauge(comment.body)
    if lang:
        bot_brain = BotBrain('command-xlarge-nightly')
        translate_text = bot_brain.translate_issue(issue.title, issue.body, lang)
        if translate_text:
            comment.edit(f"{comment.body}\n\n*ISSUE TRANSLATION*\n\n{translate_text}")
            comment.update()


def parse_translate_command_langauge(comment_text: str) -> str:
    import re
    match = re.search("@dobby translate to [\w]+", comment_text)
    words = match.group().split("to ")
    if len(words) < 2:
        return ""
    return words[-1].lower()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
