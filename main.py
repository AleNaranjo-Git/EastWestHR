from dotenv import load_dotenv
import os
from utils.logging_config import setup_logging

load_dotenv()  # Esto carga las variables del .env

# Set log level based on environment
env = os.getenv("APP_ENV", "development")
if env == "production":
    setup_logging(default_level="INFO", file_level="INFO")
else:
    setup_logging(default_level="DEBUG", file_level="INFO")

from PySide6.QtWidgets import QApplication
from ui.windows.login_window import LoginWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    app.exec()