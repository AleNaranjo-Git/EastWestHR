# pages/flc_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout,
    QDateEdit, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    INPUT_STYLE, BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, DATE_EDIT_STYLE
)
from logic.employee_logic import EmployeeLogic
from logic.auth import Session
from models.fcl_model import FCL
from datetime import date

class FCLPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.setup_ui()
        
        # Pre-fill national ID if available in session
        if Session.current_user and Session.current_user.get("cedulaEmpleado"):
            national_id = Session.current_user["cedulaEmpleado"].strip()
            self.national_id_input.setText(national_id)
            self.national_id_input.setReadOnly(True)
            self.national_id_input.setEnabled(False)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main container with limited width
        container = QWidget()
        container.setMaximumWidth(500)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(30, 30, 30, 30)

        # Main title
        title = QLabel("Solicitar FCL")
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)

        # Main form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(15)

        # National ID
        national_id_label = QLabel("Cédula:")
        national_id_label.setStyleSheet(LABEL_STYLE)
        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText("Ej: 123456789")
        self.national_id_input.setStyleSheet(INPUT_STYLE)
        self.national_id_input.setToolTip("Ingrese la cédula del trabajador")
        # Only numbers, max 9 digits
        self.national_id_input.setMaxLength(9)
        id_validator = QRegularExpressionValidator(QRegularExpression(r"^\d{0,9}$"))
        self.national_id_input.setValidator(id_validator)
        form.addRow(national_id_label, self.national_id_input)
        self.national_id_input.textChanged.connect(self.on_national_id_changed)

        # Employee name
        name_label = QLabel("Nombre:")
        name_label.setStyleSheet(LABEL_STYLE)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del trabajador")
        self.name_input.setStyleSheet(INPUT_STYLE)
        self.name_input.setToolTip("Ingrese el nombre completo del trabajador")
        form.addRow(name_label, self.name_input)
        
        # Job position
        position_label = QLabel("Cargo:")
        position_label.setStyleSheet(LABEL_STYLE)
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Cargo del trabajador")
        self.position_input.setStyleSheet(INPUT_STYLE)
        self.position_input.setToolTip("Ingrese el cargo del trabajador")
        form.addRow(position_label, self.position_input)
        
        # Hire date
        hire_date_label = QLabel("Fecha de ingreso:")
        hire_date_label.setStyleSheet(LABEL_STYLE)
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setStyleSheet(DATE_EDIT_STYLE)
        self.hire_date_input.setToolTip("Seleccione la fecha de ingreso del trabajador")
        form.addRow(hire_date_label, self.hire_date_input)

        # Max date
        max_date_label = QLabel("Fecha máxima:")
        max_date_label.setStyleSheet(LABEL_STYLE)
        self.max_date_input = QDateEdit()
        self.max_date_input.setCalendarPopup(True)
        self.max_date_input.setDate(QDate.currentDate())
        self.max_date_input.setStyleSheet(DATE_EDIT_STYLE)
        self.max_date_input.setToolTip("Seleccione la fecha máxima para la constancia")
        form.addRow(max_date_label, self.max_date_input)

        container_layout.addLayout(form)

        # Submit button
        self.submit_button = QPushButton("Solicitar Constancia")
        self.submit_button.setStyleSheet(BUTTON_STYLE)
        self.submit_button.setToolTip("Solicitar constancia de salario")
        self.submit_button.clicked.connect(self.request_fcl)
        container_layout.addWidget(self.submit_button)
        self.submit_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        main_layout.addWidget(container)
        
    def on_national_id_changed(self, text: str) -> None:
        if len(text) != 9:
            return
        employee_info = EmployeeLogic.get_employee_full_info_by_national_id(text)
        if employee_info:
            full_name = f"{employee_info['first_name'].strip()} {employee_info['last_name_1'].strip()} {employee_info['last_name_2'].strip()}"
            self.name_input.setText(full_name)
            self.position_input.setText(employee_info['position'])
            self.hire_date_input.setDate(employee_info['hire_date'])
            self.hire_date_input.setEnabled(False)
            
    def request_fcl(self) -> None:
        national_id = self.national_id_input.text().strip()
        request_date_qdate = self.max_date_input.date()
        today = QDate.currentDate()

        request_date_qdate = date(
            request_date_qdate.year(),
            request_date_qdate.month(),
            request_date_qdate.day()
        )
        
        today = date.today()
        # Validate max date
        if request_date_qdate < today:
            QMessageBox.warning(self, "Error", "No puede solicitar para una fecha pasada.")
            self.submit_button.setEnabled(True)
            return

        # Create the certificate request
        fcl_id = FCL.create_fcl(
            request_date=request_date_qdate,
            employee_national_id=national_id,
            document_generated=False
        )

        if fcl_id:
            QMessageBox.information(self, "Éxito", "Solicitud de FCL creada exitosamente.")
        else:
            QMessageBox.critical(self, "Error", "Error al crear la solicitud de FCL. Por favor, intente nuevamente.")