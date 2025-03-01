from github import Github
from github.GithubException import GithubException
from PyQt5.QtCore import QThread, pyqtSignal
import requests

class GitHubMergeExecutor(QThread):
    merge_completed = pyqtSignal(bool, str, dict)  # Added dict for additional merge info
    progress_update = pyqtSignal(str)

    def __init__(self, github_token, repo_full_name, source_branches, target_branch, commit_message, merge_method='merge'):
        super().__init__()
        self.github_token = github_token
        self.repo_full_name = repo_full_name
        self.source_branches = [item.text() for item in source_branches]
        self.target_branch = target_branch
        self.commit_message = commit_message
        self.merge_method = merge_method  # New parameter for merge strategy
        self.base_url = "https://api.github.com"
        self.owner, self.repo = repo_full_name.split('/')
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def run(self):
        try:
            self.progress_update.emit("Connecting to GitHub...")
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_full_name)
            merge_results = []

            for source_branch in self.source_branches:
                self.progress_update.emit(f"Merging {source_branch} into {self.target_branch}...")

                try:
                    # Verify branches exist
                    try:
                        source = repo.get_branch(source_branch)
                        target = repo.get_branch(self.target_branch)
                    except GithubException:
                        raise Exception(f"Branch {source_branch} or {self.target_branch} not found")

                    # Check if branches are already in sync
                    if source.commit.sha == target.commit.sha:
                        merge_results.append({
                            "branch": source_branch,
                            "status": "skipped",
                            "message": "Branches are already in sync"
                        })
                        continue

                    # Try to merge
                    merge_result = self.execute_merge(source_branch, self.target_branch)
                    merge_results.append(merge_result)

                    if merge_result['status'] == 'conflict':
                        result_info = {
                            "results": merge_results,
                            "conflict_details": merge_result
                        }
                        self.merge_completed.emit(False, f"Merge conflict in {source_branch}", result_info)
                        return

                except Exception as merge_error:
                    result_info = {
                        "results": merge_results,
                        "error": str(merge_error)
                    }
                    self.merge_completed.emit(False, str(merge_error), result_info)
                    return

            result_info = {
                "results": merge_results,
                "summary": f"Processed {len(merge_results)} branches"
            }
            self.merge_completed.emit(True, 
                f"Successfully merged {len(self.source_branches)} branches into {self.target_branch}", 
                result_info)

        except Exception as e:
            self.merge_completed.emit(False, f"Merge failed: {str(e)}", {"error": str(e)})

    def execute_merge(self, source_branch: str, target_branch: str) -> dict:
        """
        Directly merges the source branch into the target branch
        Returns a dictionary with merge status
        """
        try:
            g = Github(self.github_token)
            repo = g.get_repo(f"{self.owner}/{self.repo}")
            
            # Get the branches
            try:
                source = repo.get_branch(source_branch)
                target = repo.get_branch(target_branch)
            except GithubException:
                return {
                    'status': 'error',
                    'merged': False,
                    'message': f"Branch {source_branch} or {target_branch} not found"
                }

            # Force update target branch with source branch content
            try:
                # Get the reference to update
                ref = repo.get_git_ref(f"heads/{target_branch}")
                # Update the reference to point to the source branch's commit
                ref.edit(sha=source.commit.sha, force=True)
                
                return {
                    'status': 'success',
                    'merged': True,
                    'message': f'Successfully updated {target_branch} with content from {source_branch}'
                }
                    
            except GithubException as e:
                if e.status == 409:
                    return {
                        'status': 'conflict',
                        'merged': False,
                        'message': 'Merge conflict detected'
                    }
                return {
                    'status': 'error',
                    'merged': False,
                    'message': str(e)
                }
                    
        except Exception as e:
            return {
                'status': 'error',
                'merged': False,
                'message': str(e)
            }

    def get_conflicting_files(self, preview_data):
        """Helper method to extract conflicting files"""
        return [
            {
                'name': file.get('filename'),
                'status': file.get('status'),
                'changes': file.get('changes', 0)
            }
            for file in preview_data.get('files', [])
            if file.get('status') in ['modified', 'removed', 'added']
        ]

    def handle_merge_conflict(self, base_branch, head_branch, preview_data):
        """Handle merge conflicts with detailed information"""
        # Get detailed conflict information
        conflict_files = []
        for file in preview_data.get('files', []):
            if file.get('status') in ['modified', 'removed', 'added']:
                conflict_files.append({
                    'name': file.get('filename'),
                    'status': file.get('status'),
                    'changes': file.get('changes', 0),
                    'patch': file.get('patch', '')
                })

        return {
            "status": "conflict",
            "message": f"Merge conflict detected between {base_branch} and {head_branch}",
            "branch": head_branch,
            "conflicting_files": conflict_files,
            "compare_url": preview_data.get('html_url'),
            "resolution_options": {
                "web_url": f"https://github.com/{self.owner}/{self.repo}/compare/{base_branch}...{head_branch}",
                "command_line": [
                    f"git checkout {base_branch}",
                    f"git pull origin {base_branch}",
                    f"git merge {head_branch}",
                    "git add .",
                    'git commit -m "Resolve merge conflicts"',
                    f"git push origin {base_branch}"
                ]
            },
            "resolution_steps": [
                "1. Open the web URL to review conflicts",
                "2. Clone the repository locally if not already done",
                "3. Run the command line steps in sequence",
                "4. Resolve any conflicts in your code editor",
                "5. Complete the merge with commit and push"
            ]
        }