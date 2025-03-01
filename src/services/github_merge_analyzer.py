from github import Github
import google.generativeai as genai
from PyQt5.QtCore import QThread, pyqtSignal

class GitHubMergeAnalyzer(QThread):
    analysis_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(str)

    def __init__(self, github_token, gemini_api_key, repo_full_name, source_branch, target_branch):
        super().__init__()
        self.github_token = github_token
        self.gemini_api_key = gemini_api_key
        self.repo_full_name = repo_full_name
        self.source_branch = source_branch
        self.target_branch = target_branch

    def get_file_content(self, repo, branch, path):
        try:
            content = repo.get_contents(path, ref=branch)
            return content.decoded_content.decode('utf-8')
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def run(self):
        try:
            self.progress_update.emit("Getting repository information...")
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_full_name)

            # Compare target (main) to source (newbranch) to see what changes will be applied
            self.progress_update.emit("Comparing branches...")
            comparison = repo.compare(self.target_branch, self.source_branch)

            # Get files that were changed
            changed_files = []
            diff_text = ""

            self.progress_update.emit("Analyzing changes...")
            for file in comparison.files:
                # Get content from both branches - note the order
                target_content = self.get_file_content(repo, self.target_branch, file.filename)  # main
                source_content = self.get_file_content(repo, self.source_branch, file.filename)  # newbranch

                changed_files.append({
                    'filename': file.filename,
                    'status': file.status,
                    'additions': file.additions,
                    'deletions': file.deletions,
                    'changes': file.changes,
                    'patch': file.patch if hasattr(file, 'patch') else None,
                    'source_content': source_content,  # newbranch content
                    'target_content': target_content   # main content
                })

                if hasattr(file, 'patch') and file.patch:
                    diff_text += f"\nFile: {file.filename} ({file.status})\n"
                    diff_text += f"Changes: +{file.additions}, -{file.deletions}\n"
                    diff_text += f"Current content in {self.source_branch}:\n"  # newbranch
                    diff_text += f"{source_content}\n\n"
                    diff_text += f"Content to be merged from {self.target_branch}:\n"  # main
                    diff_text += f"{target_content}\n\n"
                    diff_text += "Changes to be applied:\n"
                    diff_text += f"{file.patch}\n\n"

            # Use AI to analyze changes
            self.progress_update.emit("Generating AI analysis...")
            ai_analysis = ""
            try:
                genai.configure(api_key=self.gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')

                prompt = f"""Analyze these changes. We want to merge from '{self.target_branch}' into '{self.source_branch}'.
The changes will update '{self.source_branch}' to match '{self.target_branch}'.

Changed files:
{[f['filename'] for f in changed_files]}

Detailed changes:
{diff_text}

Please provide:
1. A summary of what changes will be applied to '{self.source_branch}'
2. Potential risks or issues with this merge
3. Testing recommendations after merge
4. Review focus areas

Focus on how these changes will fix/update the source branch."""

                response = model.generate_content(prompt)
                ai_analysis = response.text
            except Exception as e:
                ai_analysis = f"AI analysis failed: {str(e)}"

            # Remove the test merge during comparison
            # Check for potential conflicts without merging
            has_conflicts = False
            try:
                base = repo.get_branch(self.source_branch)
                head = repo.get_branch(self.target_branch)
                # Only check if branches can be merged
                if base and head:
                    base_sha = base.commit.sha
                    head_sha = head.commit.sha
                    if base_sha != head_sha:
                        has_conflicts = repo.merging_allowed(self.source_branch, self.target_branch)
            except Exception as e:
                if "Merge conflict" in str(e):
                    has_conflicts = True

            # Prepare result
            result = {
                'repo': self.repo_full_name,
                'source_branch': self.source_branch,
                'target_branch': self.target_branch,
                'changed_files': changed_files,
                'diff_text': diff_text,
                'has_conflicts': has_conflicts,
                'ai_analysis': ai_analysis,
                'total_additions': sum(f['additions'] for f in changed_files),
                'total_deletions': sum(f['deletions'] for f in changed_files),
                'commit_count': len(comparison.commits)
            }

            self.analysis_completed.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))