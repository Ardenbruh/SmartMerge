from github import Github
from github.GithubException import GithubException
from PyQt5.QtCore import QThread, pyqtSignal

class GitHubRepoLoader(QThread):
    repos_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, github_token):
        super().__init__()
        self.github_token = github_token

    def run(self):
        try:
            g = Github(self.github_token)
            user = g.get_user()

            repos = []
            for repo in user.get_repos():
                if not repo.fork:  # Only include non-forked repos
                    repos.append({
                        'name': repo.name,
                        'full_name': repo.full_name,
                        'url': repo.html_url,
                        'description': repo.description
                    })

            self.repos_loaded.emit(repos)
        except Exception as e:
            self.error_occurred.emit(str(e))