import os
import sys
from dotenv import load_dotenv
from utils.logging_config import setup_logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.windows.main_window import MainWindow

# Function to get correct paths in the executable
def get_resource_path(relative_path: str) -> str:
    """Gets the correct path for resources, works in both development and executable."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# Function to load .env file (from filesystem in dev, from resources in executable)
def load_env_file():
    """Loads environment variables from .env file, either from filesystem or bundled resource."""
    env_path = get_resource_path(".env")
    if os.path.exists(env_path):
        # Load .env file using python-dotenv
        load_dotenv(env_path)
    else:
        print(f"Warning: .env file not found at {env_path}")

# Load environment variables
load_env_file()

# Set log level based on environment
env = os.getenv("APP_ENV", "development")
if env == "production":
    setup_logging(default_level="INFO", file_level="INFO")
else:
    setup_logging(default_level="DEBUG", file_level="INFO")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Use function to get correct icon path
    icon_path = get_resource_path("resources/icons/EW_vertical_logo_800x561.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Warning: Icon file not found at {icon_path}")
    
    try:
        main_window = MainWindow()
        main_window.show()
        app.exec()
    except Exception as e:
        print(f"Error initializing application: {str(e)}")
        sys.exit(1)