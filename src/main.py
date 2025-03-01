import sys
from PyQt5.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.config.config_manager import ConfigManager

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    config_manager = ConfigManager()
    main_window = MainWindow(config_manager)
    main_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()