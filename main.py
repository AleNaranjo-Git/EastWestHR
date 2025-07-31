from dotenv import load_dotenv
import os
import sys
from utils.logging_config import setup_logging

# Function to get correct paths in the executable
def get_resource_path(relative_path: str) -> str:
    """Gets the correct path for resources, works in both development and executable."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path: str = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        # Development - use current script directory
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

load_dotenv()

# Set log level based on environment
env = os.getenv("APP_ENV", "development")
if env == "production":
    setup_logging(default_level="INFO", file_level="INFO")
else:
    setup_logging(default_level="DEBUG", file_level="INFO")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.windows.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Use function to get correct icon path
    icon_path = get_resource_path("resources/icons/EW_vertical_logo_800x561.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    main_window = MainWindow()
    app.exec()