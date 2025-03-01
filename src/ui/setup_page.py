from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QProgressBar, QCheckBox, QGroupBox, 
    QFormLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from src.utils.api_tester import APITester

class SetupPage(QWidget):
    setup_completed = pyqtSignal(str, str)

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.init_ui()
        self.tester = None

    def init_ui(self):
        main_layout = QVBoxLayout()

        title_label = QLabel("GitHub Merge Assistant")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        desc_label = QLabel("Intelligent branch merging powered by AI")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        form_group = QGroupBox("API Configuration")
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.github_token_input = QLineEdit(self.config_manager.github_token)
        self.github_token_input.setEchoMode(QLineEdit.Password)
        self.github_token_input.setPlaceholderText("Enter your GitHub Personal Access Token")
        form_layout.addRow(QLabel("GitHub Token:"), self.github_token_input)

        self.show_github_token = QPushButton("Show")
        self.show_github_token.setCheckable(True)
        self.show_github_token.clicked.connect(self.toggle_github_token_visibility)
        form_layout.addRow("", self.show_github_token)

        self.gemini_api_input = QLineEdit(self.config_manager.gemini_api_key)
        self.gemini_api_input.setEchoMode(QLineEdit.Password)
        self.gemini_api_input.setPlaceholderText("Enter your Google Gemini API Key")
        form_layout.addRow(QLabel("Gemini API Key:"), self.gemini_api_input)

        self.show_gemini_key = QPushButton("Show")
        self.show_gemini_key.setCheckable(True)
        self.show_gemini_key.clicked.connect(self.toggle_gemini_key_visibility)
        form_layout.addRow("", self.show_gemini_key)

        self.save_creds = QCheckBox("Save credentials locally")
        self.save_creds.setChecked(True)
        form_layout.addRow("", self.save_creds)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)

        self.continue_button = QPushButton("Continue")
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(self.continue_setup)
        button_layout.addWidget(self.continue_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def toggle_github_token_visibility(self, checked):
        if checked:
            self.github_token_input.setEchoMode(QLineEdit.Normal)
            self.show_github_token.setText("Hide")
        else:
            self.github_token_input.setEchoMode(QLineEdit.Password)
            self.show_github_token.setText("Show")

    def toggle_gemini_key_visibility(self, checked):
        if checked:
            self.gemini_api_input.setEchoMode(QLineEdit.Normal)
            self.show_gemini_key.setText("Hide")
        else:
            self.gemini_api_input.setEchoMode(QLineEdit.Password)
            self.show_gemini_key.setText("Show")

    def test_connection(self):
        self.github_token = self.github_token_input.text().strip()
        self.gemini_api_key = self.gemini_api_input.text().strip()

        if not self.github_token or not self.gemini_api_key:
            self.status_label.setText("Both API keys are required")
            self.status_label.setStyleSheet("color: red;")
            return

        # Update UI to show testing
        self.status_label.setText("Testing API connections...")
        self.status_label.setStyleSheet("color: blue;")
        self.progress_bar.show()
        self.test_button.setEnabled(False)

        # Create and start the API tester thread
        self.tester = APITester(self.github_token, self.gemini_api_key)
        self.tester.test_finished.connect(self.on_test_complete)
        self.tester.start()

    def on_test_complete(self, success, github_message, gemini_message):
        self.progress_bar.hide()
        self.test_button.setEnabled(True)

        if success:
            self.status_label.setText("Connection successful! You can continue.")
            self.status_label.setStyleSheet("color: green;")
            self.continue_button.setEnabled(True)
        else:
            error_message = f"Connection failed:\n{github_message}\n{gemini_message}"
            self.status_label.setText(error_message)
            self.status_label.setStyleSheet("color: red;")
            self.continue_button.setEnabled(False)

        # Clean up the tester
        if self.tester:
            self.tester.deleteLater()
            self.tester = None

    def continue_setup(self):
        # Save configuration if requested
        if self.save_creds.isChecked():
            self.config_manager.save_config(  # Note: changed from save_credentials to save_config
                self.github_token_input.text().strip(),
                self.gemini_api_input.text().strip()
            )
        
        # Emit signal with current token values
        self.setup_completed.emit(
            self.github_token_input.text().strip(),
            self.gemini_api_input.text().strip()
        )