import requests

class GithubIssueTracker:
    def __init__(self, owner, repo, personal_access_token):
        self.owner = owner
        self.repo = repo
        self.token = personal_access_token
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

    def create_issue(self, title, body, assignees=None, milestone=None, labels=None):
        data = {
            "title": title,
            "body": body
        }
        if assignees:
            data["assignees"] = assignees
        if milestone:
            data["milestone"] = milestone
        if labels:
            data["labels"] = labels

        response = requests.post(self.base_url, headers=self.headers, json=data)
        return response
