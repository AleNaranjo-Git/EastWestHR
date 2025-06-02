from PySide6.QtWidgets import QApplication
from login_window import LoginWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    app.exec()