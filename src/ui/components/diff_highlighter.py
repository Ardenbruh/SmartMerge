# File: /github-merge-assistant/github-merge-assistant/src/ui/components/diff_highlighter.py

from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QBrush

class DiffHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

    def highlightBlock(self, text):
        format_add = QTextCharFormat()
        format_add.setBackground(QBrush(QColor("#E6FFED")))
        format_add.setForeground(QBrush(QColor("#24292E")))

        format_del = QTextCharFormat()
        format_del.setBackground(QBrush(QColor("#FFEEF0")))
        format_del.setForeground(QBrush(QColor("#24292E")))

        format_header = QTextCharFormat()
        format_header.setBackground(QBrush(QColor("#F1F8FF")))
        format_header.setForeground(QBrush(QColor("#0366D6")))

        # Highlight diff headers
        if text.startswith("@@") and text.find("@@", 2) > 0:
            self.setFormat(0, len(text), format_header)
        # Highlight additions
        elif text.startswith("+"):
            self.setFormat(0, len(text), format_add)
        # Highlight deletions
        elif text.startswith("-"):
            self.setFormat(0, len(text), format_del)