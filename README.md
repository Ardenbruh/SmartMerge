# README.md

# SmartMerge

The SmartMerge Assistant is a Python application designed to facilitate intelligent branch merging on GitHub. It leverages AI to analyze changes between branches and provides a user-friendly interface for managing merge operations.

## Features

- Connects to GitHub and loads repositories and branches.
- Analyzes differences between branches and checks for potential merge conflicts.
- Provides AI-generated insights and recommendations for merges.
- User-friendly interface built with PyQt5.

## Requirements

- Python 3.x
- PyQt5
- PyGithub
- google-generativeai

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/github-merge-assistant.git
   ```

2. Navigate to the project directory:

   ```
   cd github-merge-assistant
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

## Usage

1. Set up your GitHub Personal Access Token and Gemini API Key in the application.
2. Launch the application:

   ```
   python src/main.py
   ```

3. Follow the on-screen instructions to select repositories and branches for merging.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.