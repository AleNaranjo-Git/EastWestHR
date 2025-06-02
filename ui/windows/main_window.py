from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de RRHH")
        self.resize(1100, 700)
        self.showMaximized()
        self.setStyleSheet("background-color: white;")
