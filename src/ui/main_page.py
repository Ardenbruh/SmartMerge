from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QListWidget, QTextEdit, QTabWidget, QProgressBar, 
    QMessageBox, QFormLayout, QDialog, QListWidgetItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from src.services.github_repo_loader import GitHubRepoLoader
from src.services.github_branch_loader import GitHubBranchLoader
from src.services.github_merge_analyzer import GitHubMergeAnalyzer
from src.services.github_merge_executor import GitHubMergeExecutor
from src.ui.components.diff_highlighter import DiffHighlighter
from src.ui.merge_dialog import MergeDialog

class MainPage(QWidget):
    def __init__(self, github_token, gemini_api_key):
        super().__init__()
        self.github_token = github_token
        self.gemini_api_key = gemini_api_key
        self.current_repo = None
        self.init_ui()
        self.load_repos()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        title_label = QLabel("GitHub Merge Assistant")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(self.status_label)

        main_layout.addLayout(header_layout)

        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("Repository:"))

        self.repo_combo = QComboBox()
        self.repo_combo.setMinimumWidth(300)
        self.repo_combo.currentIndexChanged.connect(self.on_repo_selected)
        repo_layout.addWidget(self.repo_combo)

        self.refresh_repos_button = QPushButton("Refresh")
        self.refresh_repos_button.clicked.connect(self.load_repos)
        repo_layout.addWidget(self.refresh_repos_button)

        repo_layout.addStretch()
        main_layout.addLayout(repo_layout)

        branch_layout = QHBoxLayout()
        branch_form = QFormLayout()
        branch_form.setSpacing(10)

        self.target_branch_combo = QComboBox()
        branch_form.addRow("Target Branch:", self.target_branch_combo)

        self.source_branches_list = QListWidget()
        self.source_branches_list.setSelectionMode(QListWidget.ExtendedSelection)
        branch_form.addRow("Source Branches:", self.source_branches_list)

        branch_form_widget = QWidget()
        branch_form_widget.setLayout(branch_form)
        branch_layout.addWidget(branch_form_widget)

        self.compare_button = QPushButton("Compare Branches")
        self.compare_button.setEnabled(False)
        self.compare_button.clicked.connect(self.analyze_merge)
        branch_layout.addWidget(self.compare_button)

        main_layout.addLayout(branch_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        self.progress_status = QLabel()
        self.progress_status.hide()
        main_layout.addWidget(self.progress_status)

        self.results_tabs = QTabWidget()
        self.results_tabs.hide()

        self.ai_analysis_widget = QWidget()
        ai_layout = QVBoxLayout()

        self.ai_analysis_text = QTextEdit()
        self.ai_analysis_text.setReadOnly(True)
        ai_layout.addWidget(self.ai_analysis_text)

        self.ai_analysis_widget.setLayout(ai_layout)
        self.results_tabs.addTab(self.ai_analysis_widget, "AI Analysis")

        self.diff_widget = QWidget()
        diff_layout = QVBoxLayout()

        self.diff_summary = QLabel()
        diff_layout.addWidget(self.diff_summary)

        self.diff_text = QTextEdit()
        self.diff_text.setReadOnly(True)
        self.diff_text.setFont(QFont("Courier New", 10))
        self.diff_highlighter = DiffHighlighter(self.diff_text.document())
        diff_layout.addWidget(self.diff_text)

        self.diff_widget.setLayout(diff_layout)
        self.results_tabs.addTab(self.diff_widget, "Changes")

        self.files_widget = QWidget()
        files_layout = QVBoxLayout()

        self.files_list = QListWidget()
        self.files_list.itemClicked.connect(self.on_file_selected)
        files_layout.addWidget(self.files_list)

        self.files_widget.setLayout(files_layout)
        self.results_tabs.addTab(self.files_widget, "Changed Files")

        main_layout.addWidget(self.results_tabs)

        self.merge_button = QPushButton("Merge Branches")
        self.merge_button.setStyleSheet("background-color: #2EA44F; color: white; font-weight: bold; padding: 10px;")
        self.merge_button.setMinimumHeight(40)
        self.merge_button.hide()
        self.merge_button.clicked.connect(self.execute_merge)
        main_layout.addWidget(self.merge_button)

        self.setLayout(main_layout)

    def load_repos(self):
        self.status_label.setText("Loading repositories...")
        self.repo_combo.clear()
        self.source_branches_list.clear()
        self.target_branch_combo.clear()
        self.compare_button.setEnabled(False)

        self.progress_bar.show()

        self.repo_loader = GitHubRepoLoader(self.github_token)
        self.repo_loader.repos_loaded.connect(self.on_repos_loaded)
        self.repo_loader.error_occurred.connect(self.on_error)
        self.repo_loader.start()

    def on_repos_loaded(self, repos):
        self.progress_bar.hide()
        self.status_label.setText(f"Found {len(repos)} repositories")

        self.repos = repos

        for repo in repos:
            self.repo_combo.addItem(repo['full_name'], repo)

    def on_repo_selected(self, index):
        if index >= 0:
            self.current_repo = self.repos[index]
            self.load_branches()

    def load_branches(self):
        if not self.current_repo:
            return

        self.source_branches_list.clear()
        self.target_branch_combo.clear()
        self.compare_button.setEnabled(False)

        self.progress_bar.show()
        self.status_label.setText(f"Loading branches for {self.current_repo['full_name']}...")

        self.branch_loader = GitHubBranchLoader(self.github_token, self.current_repo['full_name'])
        self.branch_loader.branches_loaded.connect(self.on_branches_loaded)
        self.branch_loader.error_occurred.connect(self.on_error)
        self.branch_loader.start()

    def on_branches_loaded(self, branches):
        self.progress_bar.hide()
        self.status_label.setText(f"Found {len(branches)} branches")

        self.branches = branches

        self.target_branch_combo.clear()
        self.source_branches_list.clear()

        for branch in branches:
            self.target_branch_combo.addItem(branch['name'])
            self.source_branches_list.addItem(branch['name'])

        self.compare_button.setEnabled(True)

    def analyze_merge(self):
        selected_items = self.source_branches_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Invalid Selection", "Please select at least one source branch")
            return

        source_branches = [item.text() for item in selected_items]
        target_branch = self.target_branch_combo.currentText()

        if target_branch in source_branches:
            QMessageBox.warning(self, "Invalid Selection", "Target branch cannot be in source branches")
            return

        self.progress_bar.show()
        self.progress_status.show()
        self.progress_status.setText("Starting analysis...")
        self.compare_button.setEnabled(False)
        self.merge_button.hide()
        self.results_tabs.hide()

        self.current_analysis_results = []
        self.analyze_next_branch(source_branches, target_branch)

    def analyze_next_branch(self, remaining_branches, target_branch):
        if not remaining_branches:
            self.show_combined_results()
            return

        source_branch = remaining_branches[0]

        self.analyzer = GitHubMergeAnalyzer(
            self.github_token,
            self.gemini_api_key,
            self.current_repo['full_name'],
            source_branch,
            target_branch
        )
        self.analyzer.progress_update.connect(self.update_progress)
        self.analyzer.analysis_completed.connect(
            lambda result: self.on_branch_analysis_complete(result, remaining_branches[1:], target_branch)
        )
        self.analyzer.error_occurred.connect(self.on_error)
        self.analyzer.start()

    def on_branch_analysis_complete(self, result, remaining_branches, target_branch):
        self.current_analysis_results.append(result)
        if remaining_branches:
            self.analyze_next_branch(remaining_branches, target_branch)
        else:
            self.show_combined_results()

    def show_combined_results(self):
        self.progress_bar.hide()
        self.progress_status.hide()
        self.compare_button.setEnabled(True)

        # Combine results from all analyzed branches
        total_commits = sum(r['commit_count'] for r in self.current_analysis_results)
        total_additions = sum(r['total_additions'] for r in self.current_analysis_results)
        total_deletions = sum(r['total_deletions'] for r in self.current_analysis_results)
        has_conflicts = any(r['has_conflicts'] for r in self.current_analysis_results)

        # Update summary
        summary = (
            f"Total Changes: {total_commits} commits, "
            f"+{total_additions} additions, "
            f"-{total_deletions} deletions\n"
        )
        if has_conflicts:
            summary += "⚠️ Some merges have conflicts that need to be resolved!"
        self.diff_summary.setText(summary)

        # Show combined diff text
        combined_diff = ""
        for result in self.current_analysis_results:
            combined_diff += f"\n=== Changes in {result['source_branch']} ===\n\n"
            combined_diff += result['diff_text']
        
        self.diff_text.setText(combined_diff)

        # Show all changed files
        self.files_list.clear()
        for result in self.current_analysis_results:
            branch_name = result['source_branch']
            for file in result['changed_files']:
                item = QListWidgetItem()
                item.setText(
                    f"[{branch_name}] {file['filename']} "
                    f"(+{file['additions']}, -{file['deletions']})"
                )
                item.setData(Qt.UserRole, {
                    'branch': branch_name,
                    'file': file
                })
                self.files_list.addItem(item)

        # Combine AI analysis
        combined_analysis = ""
        for result in self.current_analysis_results:
            combined_analysis += f"\n=== Analysis for {result['source_branch']} ===\n\n"
            combined_analysis += result['ai_analysis']
            combined_analysis += "\n\n"
        
        self.ai_analysis_text.setText(combined_analysis)

        # Show results and merge button
        self.results_tabs.show()
        if not has_conflicts:
            self.merge_button.show()

    def on_file_selected(self, item):
        data = item.data(Qt.UserRole)
        if data and 'file' in data:
            file_data = data['file']
            if file_data.get('patch'):
                diff_text = (
                    f"Branch: {data['branch']}\n"
                    f"File: {file_data['filename']} ({file_data['status']})\n"
                    f"Changes: +{file_data['additions']}, -{file_data['deletions']}\n\n"
                    f"{file_data['patch']}"
                )
                self.diff_text.setText(diff_text)
                self.results_tabs.setCurrentWidget(self.diff_widget)

    def execute_merge(self):
        selected_items = self.source_branches_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Invalid Selection", "Please select at least one source branch")
            return

        dialog = MergeDialog(
            self,
            self.current_repo['full_name'],
            [item.text() for item in selected_items],
            self.target_branch_combo.currentText()
        )

        if dialog.exec_() == QDialog.Accepted:
            self.progress_bar.show()
            self.progress_status.show()
            self.progress_status.setText("Executing merge...")
            self.merge_button.setEnabled(False)

            self.merger = GitHubMergeExecutor(
                self.github_token,
                self.current_repo['full_name'],
                selected_items,
                self.target_branch_combo.currentText(),
                dialog.get_commit_message()
            )
            self.merger.progress_update.connect(self.update_progress)
            self.merger.merge_completed.connect(self.on_merge_complete)
            self.merger.start()

    def on_merge_complete(self, success, message):
        self.progress_bar.hide()
        self.progress_status.hide()
        self.merge_button.setEnabled(True)

        if success:
            QMessageBox.information(self, "Success", message)
            self.load_branches()
        else:
            QMessageBox.warning(self, "Merge Failed", message)

    def on_error(self, error_message):
        self.progress_bar.hide()
        self.progress_status.hide()
        self.compare_button.setEnabled(True)
        QMessageBox.critical(self, "Error", str(error_message))

    def update_progress(self, message):
        self.progress_status.setText(message)
        self.progress_status.show()