import os
import requests

from dotenv import load_dotenv
from flask import Flask, request
from github import Github, GithubIntegration


load_dotenv()
app = Flask(__name__)
# app id
app_id = os.getenv('APP_ID')
# Read the bot certificate
with open(
        os.get_env('PATH_TO_CERT'),
        'r'
) as cert_file:
    app_key = cert_file.read()

# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)


@app.route("/", methods=['POST'])
def bot():
    
    # exit if not an issue event 
    if not all(k in payload.keys() for k in ['action', 'issue']) and \
            payload['action'] == 'opened':
        return "ok"

    payload = request.json
    owner = payload['repository']['owner']['login']
    repo_name = payload['repository']['name']
    issue_number = payload['issue']['number']

    # Get a git connection as our bot
    # Here is where we are getting the permission to talk as our bot and not
    # as a Python webservice
    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id
        ).token
    )
    repo = git_connection.get_repo(f"{owner}/{repo_name}")

    issue = repo.get_issue(number=1)

    print(issue.body)


if __name__ == "__main__":
    app.run(debug=True, port=5000)