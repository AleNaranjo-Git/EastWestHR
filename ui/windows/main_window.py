from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QVBoxLayout
from ui.components.menu_sidebar import MenuSidebar
from resources.styles.colors import BACKGROUND
from ui.pages.vacations_page import VacationsPage
from ui.pages.permits_page import PermitsPage
from ui.pages.salary_certificate_page import SalaryCertificatePage
from ui.pages.fcl_page import FCLPage
from ui.pages.pending_request_page import PendingRequestPage
from ui.pages.document_request_page import DocumentRequestPage
from ui.pages.report_generation_page import ReportGenerationPage
from logic.auth import get_current_user_role, Session

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de RRHH")
        self.resize(1100, 700)

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.menu = MenuSidebar(self)
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

        # Pages that always load
        self.vacations_page = VacationsPage()
        self.permits_page = PermitsPage()
        self.salary_certificate = SalaryCertificatePage()
        self.fcl_page = FCLPage()

        self.stack.addWidget(self.vacations_page)
        self.stack.addWidget(self.permits_page)
        self.stack.addWidget(self.salary_certificate)
        self.stack.addWidget(self.fcl_page)

        # Sidebar buttons for always-loaded pages
        self.menu.buttons["Vacaciones"].clicked.connect(lambda: self.stack.setCurrentWidget(self.vacations_page))
        self.menu.buttons["Permisos"].clicked.connect(lambda: self.stack.setCurrentWidget(self.permits_page))
        self.menu.buttons["Constancia"].clicked.connect(lambda: self.stack.setCurrentWidget(self.salary_certificate))
        self.menu.buttons["FCL"].clicked.connect(lambda: self.stack.setCurrentWidget(self.fcl_page))

        # Pages that require specific roles
        user_role = get_current_user_role() if Session.current_user else None
        if user_role in (1, 2, 3):
            self.pending_requests_page = PendingRequestPage()
            self.stack.addWidget(self.pending_requests_page)
            self.menu.buttons["Pendiente Aprobar"].clicked.connect(lambda: self.stack.setCurrentWidget(self.pending_requests_page))
        else:
            self.menu.buttons["Pendiente Aprobar"].setVisible(False)

        if user_role in (1, 3):
            self.document_request_page = DocumentRequestPage()
            self.report_generation_page = ReportGenerationPage()
            self.stack.addWidget(self.document_request_page)
            self.stack.addWidget(self.report_generation_page)
            self.menu.buttons["Generar Documento"].clicked.connect(lambda: self.stack.setCurrentWidget(self.document_request_page))
            self.menu.buttons["Generar Reporte"].clicked.connect(lambda: self.stack.setCurrentWidget(self.report_generation_page))
        else:
            self.menu.buttons["Generar Documento"].setVisible(False)
            self.menu.buttons["Generar Reporte"].setVisible(False)

        self.showMaximized()