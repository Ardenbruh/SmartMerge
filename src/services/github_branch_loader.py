# src/services/github_branch_loader.py

from github import Github
from github.GithubException import GithubException
from PyQt5.QtCore import QThread, pyqtSignal

class GitHubBranchLoader(QThread):
    branches_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, github_token, repo_full_name):
        super().__init__()
        self.github_token = github_token
        self.repo_full_name = repo_full_name

    def run(self):
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_full_name)

            branches = []
            for branch in repo.get_branches():
                branches.append({
                    'name': branch.name,
                    'sha': branch.commit.sha,
                    'protected': branch.protected
                })

            self.branches_loaded.emit(branches)
        except Exception as e:
            self.error_occurred.emit(str(e))