# pages/constancia_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout,
    QSizePolicy, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    INPUT_STYLE, BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, DATE_EDIT_STYLE, MESSAGE_BOX_STYLE
)
from logic.employee_logic import EmployeeLogic
from logic.auth import Session
from models.salary_certificate_model import SalaryCertificate
from datetime import date
from utils.dialog_utils import show_critical_dialog, show_information_dialog, show_warning_dialog

class SalaryCertificatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.setup_ui()
        
        # Pre-fill national ID if available in session
        if Session.current_user and Session.current_user.get("cedulaEmpleado"):
            national_id = Session.current_user["cedulaEmpleado"].strip()
            self.national_id_input.setText(national_id)

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
        title = QLabel("Solicitar Constancia de Salario")
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)

        # Main form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(15)

        # --- Form fields ---
        # National ID
        national_id_label = QLabel("Identificación:")
        national_id_label.setStyleSheet(LABEL_STYLE)
        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText("Ej: 123456789 o 123456789012")
        self.national_id_input.setStyleSheet(INPUT_STYLE)
        self.national_id_input.setToolTip("Ingrese la cédula (9 dígitos) o DIMEX (12 dígitos)")
        # Allow up to 12 digits
        self.national_id_input.setMaxLength(12)
        # Only numbers, allow 9 or 12 digits
        id_validator = QRegularExpressionValidator(QRegularExpression(r"^\d{9}|\d{12}$"))
        self.national_id_input.setValidator(id_validator)
        form.addRow(national_id_label, self.national_id_input)
        self.national_id_input.textChanged.connect(self.on_national_id_changed)

        # Employee name
        name_label = QLabel("Nombre completo:")
        name_label.setStyleSheet(LABEL_STYLE)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre completo")
        self.name_input.setStyleSheet(INPUT_STYLE)
        self.name_input.setToolTip("Ingrese el nombre completo")
        # Only letters and spaces
        name_validator = QRegularExpressionValidator(QRegularExpression(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]*$"))
        self.name_input.setValidator(name_validator)
        form.addRow(name_label, self.name_input)
        
        # Job position
        position_label = QLabel("Cargo:")
        position_label.setStyleSheet(LABEL_STYLE)
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Cargo del colaborador")
        self.position_input.setStyleSheet(INPUT_STYLE)
        self.position_input.setToolTip("Ingrese el cargo del colaborador")
        form.addRow(position_label, self.position_input)
        
        # Hire date
        hire_date_label = QLabel("Fecha de ingreso:")
        hire_date_label.setStyleSheet(LABEL_STYLE)
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setStyleSheet(DATE_EDIT_STYLE)
        self.hire_date_input.setToolTip("Seleccione la fecha de ingreso del colaborador")
        form.addRow(hire_date_label, self.hire_date_input)

        # Max date
        max_date_label = QLabel("Fecha límite de entrega:")
        max_date_label.setStyleSheet(LABEL_STYLE)
        self.max_date_input = QDateEdit()
        self.max_date_input.setCalendarPopup(True)
        self.max_date_input.setDate(QDate.currentDate())
        self.max_date_input.setStyleSheet(DATE_EDIT_STYLE)
        self.max_date_input.setToolTip("Seleccione la fecha límite de entrega")
        form.addRow(max_date_label, self.max_date_input)

        container_layout.addLayout(form)

        # Submit button
        self.submit_button = QPushButton("Solicitar Constancia")
        self.submit_button.setStyleSheet(BUTTON_STYLE)
        self.submit_button.setToolTip("Solicitar constancia de salario")
        self.submit_button.clicked.connect(self.request_certificate)
        container_layout.addWidget(self.submit_button)
        self.submit_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        main_layout.addWidget(container)
    
    def on_national_id_changed(self, text: str) -> None:
        # Check if the input is either 9 or 12 digits
        if len(text) not in (9, 12) or not text.isdigit():
            self.name_input.clear()
            self.position_input.clear()
            return
        employee_info = EmployeeLogic.get_employee_full_info_by_national_id(text)
        if employee_info:
            full_name = f"{employee_info['first_name'].strip()} {employee_info['last_name_1'].strip()} {employee_info['last_name_2'].strip()}"
            self.name_input.setText(full_name)
            self.position_input.setText(employee_info['position'])
            self.hire_date_input.setDate(employee_info['hire_date'])
            self.hire_date_input.setEnabled(False)

    def request_certificate(self) -> None:
         # Show confirmation dialog before proceeding
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Confirmar solicitud")
        confirmation.setText("¿Está seguro/a que toda la información introducida es correcta?")
        confirmation.setStyleSheet(MESSAGE_BOX_STYLE)

        yes_button = confirmation.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        confirmation.addButton("No", QMessageBox.ButtonRole.NoRole)
        confirmation.setDefaultButton(yes_button)

        confirmation.exec()
        if confirmation.clickedButton() != yes_button:
            return

        # National ID validation
        national_id = self.national_id_input.text().strip()
        if not national_id.isdigit() or len(national_id) not in (9, 12):
            show_warning_dialog(self, "Error", "La identificación debe contener exactamente 9 o 12 números.")
            self.submit_button.setEnabled(True)
            return

        # Check if the national ID is valid
        employee_info = EmployeeLogic.get_employee_full_info_by_national_id(national_id)
        if not employee_info:
            show_warning_dialog(self, "Error", "La identificación ingresada no corresponde a un colaborador válido.")
            self.submit_button.setEnabled(True)
            return

        # Name validation
        name = self.name_input.text().strip()
        if not name or not all(c.isalpha() or c.isspace() for c in name):
            show_warning_dialog(self, "Error", "El nombre solo puede contener letras y espacios.")
            self.submit_button.setEnabled(True)
            return
        
         # Position validation
        position = self.position_input.text().strip()
        if not position:
            show_warning_dialog(self, "Error", "El campo 'Cargo' no puede estar vacío.")
            self.submit_button.setEnabled(True)
            return

        # Hire date validation
        hire_date_qdate = self.hire_date_input.date()
        hire_date = date(hire_date_qdate.year(), hire_date_qdate.month(), hire_date_qdate.day())
        today = date.today()
        if hire_date > today:
            show_warning_dialog(self, "Error", "La fecha de ingreso no puede ser una fecha futura.")
            self.submit_button.setEnabled(True)
            return

        # Max date validation
        max_date_qdate = self.max_date_input.date()
        max_date = date(max_date_qdate.year(), max_date_qdate.month(), max_date_qdate.day())
        if max_date < today:
            show_warning_dialog(self, "Error", "La fecha límite de entrega no puede ser una fecha pasada.")
            self.submit_button.setEnabled(True)
            return
        
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
            show_warning_dialog(self, "Error", "No puede solicitar para una fecha pasada.")
            self.submit_button.setEnabled(True)
            return

        # Create the certificate request
        certificate_id = SalaryCertificate.create_certificate(
            request_date=request_date_qdate,
            employee_national_id=national_id,
            document_generated=False
        )

        if certificate_id:
            show_information_dialog(self, "Éxito", "Solicitud de constancia salarial solicitado exitosamente.")
            self.reset_form()
        else:
            show_critical_dialog(self, "Error", "Error al crear la solicitud de constancia de salario. Por favor, intente nuevamente.")

    def reset_form(self):
        """
        Resets all form fields to their default values.
        """
        # Reset National ID (if editable)
        if not self.national_id_input.isReadOnly():
            self.national_id_input.clear()

        # Reset name
        self.name_input.clear()

        # Reset position
        self.position_input.clear()

        # Reset hire date to today
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setEnabled(True)

        # Reset max date to today
        self.max_date_input.setDate(QDate.currentDate())