# File: /github-merge-assistant/github-merge-assistant/src/ui/merge_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QFrame

class MergeDialog(QDialog):
    def __init__(self, parent=None, repo_name="", source_branches=None, target_branch=""):
        super().__init__(parent)
        self.setWindowTitle("Confirm Merge")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Info label
        branches_text = ", ".join(source_branches) if source_branches else ""
        info_text = f"You are about to merge branches <b>{branches_text}</b> into <b>{target_branch}</b> in repository <b>{repo_name}</b>."
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Warning
        warning = QLabel("This action cannot be undone. Please make sure you've reviewed the changes.")
        warning.setStyleSheet("color: #E36209;")
        layout.addWidget(warning)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Commit message
        layout.addWidget(QLabel("Commit Message:"))
        self.commit_message = QTextEdit()
        self.commit_message.setPlainText(f"Merge branches {branches_text} into {target_branch}")
        self.commit_message.setMaximumHeight(100)
        layout.addWidget(self.commit_message)

        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.merge_button = QPushButton("Merge Branches")
        self.merge_button.setStyleSheet("background-color: #2EA44F; color: white;")
        self.merge_button.clicked.connect(self.accept)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.merge_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_commit_message(self):
        return self.commit_message.toPlainText()