from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QVBoxLayout
from ui.components.menu_sidebar import MenuSidebar
from resources.styles.colors import BACKGROUND
from ui.pages.vacations_page import VacationsPage
from ui.pages.permits_page import PermitsPage
from ui.pages.salary_certificate_page import SalaryCertificatePage
from ui.pages.fcl_page import FCLPage
from ui.pages.pending_request_page import PendingRequestPage
from logic.auth import get_current_user_role

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
        self.permits_page = PermitsPage()
        self.salary_certificate = SalaryCertificatePage()
        self.fcl_page = FCLPage()
        self.pending_requests_page = PendingRequestPage()

        self.stack.addWidget(self.vacations_page)
        self.stack.addWidget(self.permits_page)
        self.stack.addWidget(self.salary_certificate)
        self.stack.addWidget(self.fcl_page)
        self.stack.addWidget(self.pending_requests_page)
        
        self.menu.buttons["Vacaciones"].clicked.connect(lambda: self.stack.setCurrentWidget(self.vacations_page))
        self.menu.buttons["Permisos"].clicked.connect(lambda: self.stack.setCurrentWidget(self.permits_page))
        self.menu.buttons["Constancia"].clicked.connect(lambda: self.stack.setCurrentWidget(self.salary_certificate))
        self.menu.buttons["FCL"].clicked.connect(lambda: self.stack.setCurrentWidget(self.fcl_page))

        # Only allow roles 1, 2, 3 to see "Pendiente Aprobar"
        user_role = get_current_user_role()
        if user_role in (1, 2, 3):
            self.menu.buttons["Pendiente Aprobar"].clicked.connect(lambda: self.stack.setCurrentWidget(self.pending_requests_page))
        else:
            self.menu.buttons["Pendiente Aprobar"].setVisible(False)