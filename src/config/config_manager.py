import os
import json

class ConfigManager:
    def __init__(self):
        self.config_path = os.path.expanduser("~/.github_merge_assistant.json")
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.load_config()

    def load_config(self):
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.github_token = config.get('github_token', self.github_token)
                    self.gemini_api_key = config.get('gemini_api_key', self.gemini_api_key)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self, github_token, gemini_api_key):
        """Save current configuration to file"""
        self.github_token = github_token
        self.gemini_api_key = gemini_api_key

        try:
            with open(self.config_path, 'w') as f:
                json.dump({
                    'github_token': github_token,
                    'gemini_api_key': gemini_api_key
                }, f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False