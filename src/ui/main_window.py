from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from src.ui.setup_page import SetupPage
from src.ui.main_page import MainPage

class MainWindow(QMainWindow):
    def __init__(self, config_manager):
        super().__init__()
        self.setWindowTitle("SmartMerge")
        self.setMinimumSize(800, 600)

        self.config_manager = config_manager
        
        # Create stacked widget to manage pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create setup page
        self.setup_page = SetupPage(self.config_manager)
        self.setup_page.setup_completed.connect(self.on_setup_complete)
        self.stacked_widget.addWidget(self.setup_page)

    def on_setup_complete(self, github_token, gemini_api_key):
        try:
            # Create and show main page
            self.main_page = MainPage(github_token, gemini_api_key)
            self.stacked_widget.addWidget(self.main_page)
            self.stacked_widget.setCurrentWidget(self.main_page)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize main page: {str(e)}")

    def handle_merge_button_clicked(self):
        source_branch = self.source_branch_combo.currentText()
        target_branch = self.target_branch_combo.currentText()
        
        try:
            result = self.github_merge_executor.execute_merge(source_branch, target_branch)
            
            if result['status'] == 'success':
                QMessageBox.information(self, "Success", 
                    f"Successfully updated {target_branch} with content from {source_branch}")
            else:
                QMessageBox.critical(self, "Error", f"Operation failed: {result['message']}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Operation failed: {str(e)}")