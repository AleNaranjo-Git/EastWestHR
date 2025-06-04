from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QVBoxLayout
from ui.components.menu_sidebar import MenuSidebar
from resources.styles.colors import BACKGROUND
from ui.pages.vacations_page import VacationsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de RRHH")
        self.resize(1100, 700)
        self.showMaximized()

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.menu = MenuSidebar()
        main_layout.addWidget(self.menu)
        
        # Container for the central area
        central_area = QWidget()
        central_area.setStyleSheet(f"background-color: {BACKGROUND};")
        area_layout = QVBoxLayout(central_area)
        area_layout.setContentsMargins(0, 0, 0, 0)
        area_layout.setSpacing(0)

        self.stack = QStackedWidget()
        area_layout.addWidget(self.stack)
        main_layout.addWidget(central_area)
        
        # Pages
        self.vacations_page = VacationsPage()
        
        self.stack.addWidget(self.vacations_page)
        
        self.menu.buttons["Vacaciones"].clicked.connect(lambda: self.stack.setCurrentWidget(self.vacations_page))