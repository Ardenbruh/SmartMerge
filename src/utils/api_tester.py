from PyQt5.QtCore import QThread, pyqtSignal
from github import Github
import google.generativeai as genai

class APITester(QThread):
    test_finished = pyqtSignal(bool, str, str)

    def __init__(self, github_token, gemini_api_key):
        super().__init__()
        self.github_token = github_token
        self.gemini_api_key = gemini_api_key

    def run(self):
        try:
            # Test GitHub connection
            github_success, github_message = self.test_github_token()
            
            # Test Gemini connection
            gemini_success, gemini_message = self.test_gemini_api()
            
            # Emit results
            self.test_finished.emit(
                github_success and gemini_success,
                github_message,
                gemini_message
            )
        except Exception as e:
            self.test_finished.emit(False, "Test failed", str(e))

    def test_github_token(self):
        try:
            g = Github(self.github_token)
            # Test authentication explicitly
            user = g.get_user()
            # Force a request to verify credentials
            username = user.login
            return True, f"GitHub: Connected as {username}"
        except Exception as e:
            if "401" in str(e):
                return False, "GitHub: Invalid token or insufficient permissions"
            return False, f"GitHub Error: {str(e)}"

    def test_gemini_api(self):
        try:
            genai.configure(api_key=self.gemini_api_key)
            # Update model to gemini-2.0-flash
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            # Simple test prompt
            response = model.generate_content("Hello")
            return True, "Gemini: Connection successful"
        except Exception as e:
            return False, f"Gemini Error: Please check your API key and try again"