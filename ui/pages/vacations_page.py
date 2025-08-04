from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout,
    QDateEdit, QSizePolicy, QSpacerItem, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    INPUT_STYLE, BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, DATE_EDIT_STYLE
)
from models.employee_model import Employee
from logic.auth import Session
from logic.email_service import send_email, fetch_recipients
from datetime import date
import logging
from resources.styles.components import MESSAGE_BOX_STYLE
from utils.dialog_utils import show_information_dialog, show_warning_dialog, show_critical_dialog

class VacationsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.employee_info = None
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.setup_ui()
        self.showMaximized()

        # Pre-fill national ID if available in session
        if Session.current_user and Session.current_user.get("cedulaEmpleado"):
            national_id = Session.current_user["cedulaEmpleado"].strip()
            self.national_id_input.setText(national_id)
            
        # Calculate the week number for the request date
        self.calculate_week()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main container with limited width
        container = QWidget()
        container.setMaximumWidth(1200)
        container.setMaximumHeight(800)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(30, 30, 30, 30)

        # Main title
        title = QLabel("Solicitar Vacación")
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
        employee_name_label = QLabel("Nombre completo:")
        employee_name_label.setStyleSheet(LABEL_STYLE)
        self.employee_name_input = QLineEdit()
        self.employee_name_input.setPlaceholderText("Nombre completo")
        self.employee_name_input.setStyleSheet(INPUT_STYLE)
        self.employee_name_input.setToolTip("Ingrese el nombre completo")
        # Only letters and spaces
        name_validator = QRegularExpressionValidator(QRegularExpression(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]*$"))
        self.employee_name_input.setValidator(name_validator)
        form.addRow(employee_name_label, self.employee_name_input)

        # Request date
        request_date_label = QLabel("Fecha de solicitud:")
        request_date_label.setStyleSheet(LABEL_STYLE)
        self.request_date_input = QDateEdit()
        self.request_date_input.setCalendarPopup(True)
        self.request_date_input.setDate(QDate.currentDate())
        self.request_date_input.setStyleSheet(DATE_EDIT_STYLE)
        self.request_date_input.setToolTip("Seleccione la fecha de solicitud")
        self.request_date_input.setReadOnly(True)
        self.request_date_input.setEnabled(False)
        form.addRow(request_date_label, self.request_date_input)

        # Vacation start date
        vacation_start_label = QLabel("Fecha de inicio vacaciones:")
        vacation_start_label.setStyleSheet(LABEL_STYLE)
        self.vacation_start_input = QDateEdit()
        self.vacation_start_input.setCalendarPopup(True)
        self.vacation_start_input.setDate(QDate.currentDate())
        self.vacation_start_input.setStyleSheet(DATE_EDIT_STYLE)
        self.vacation_start_input.setToolTip("Seleccione la fecha inicio de las vacaciones")
        form.addRow(vacation_start_label, self.vacation_start_input)
        self.vacation_start_input.dateChanged.connect(self.calculate_week)

        # Vacation end date
        vacation_end_label = QLabel("Fecha final de vacaciones:")
        vacation_end_label.setStyleSheet(LABEL_STYLE)
        self.vacation_end_input = QDateEdit()
        self.vacation_end_input.setCalendarPopup(True)
        self.vacation_end_input.setDate(QDate.currentDate())
        self.vacation_end_input.setStyleSheet(DATE_EDIT_STYLE)
        self.vacation_end_input.setToolTip("Seleccione la fecha final de las vacaciones")
        form.addRow(vacation_end_label, self.vacation_end_input)

        # Vacation status (system default, read-only)
        status_label = QLabel("Estado de la solicitud:")
        status_label.setStyleSheet(LABEL_STYLE)
        self.status_input = QLineEdit()
        self.status_input.setText("Pendiente")
        self.status_input.setStyleSheet(INPUT_STYLE)
        self.status_input.setToolTip("Estado de la solicitud")
        self.status_input.setReadOnly(True)
        self.status_input.setEnabled(False)
        form.addRow(status_label, self.status_input)

        # Supervisor approval
        supervisor_label = QLabel("Aprobado por:")
        supervisor_label.setStyleSheet(LABEL_STYLE)
        self.supervisor_input = QLineEdit()
        self.supervisor_input.setPlaceholderText("Nombre de quien aprueba")
        self.supervisor_input.setStyleSheet(INPUT_STYLE)
        self.supervisor_input.setToolTip("Nombre de la persona que aprueba")
        self.supervisor_input.setReadOnly(True)
        self.supervisor_input.setEnabled(False)
        form.addRow(supervisor_label, self.supervisor_input)

        # Week number label
        self.week_label = QLabel("Semana #: -")
        self.week_label.setStyleSheet(LABEL_STYLE)
        self.week_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        form.addRow(self.week_label)

        container_layout.addLayout(form)

        # Submit button
        self.submit_button = QPushButton("Solicitar Vacación")
        self.submit_button.setStyleSheet(BUTTON_STYLE)
        self.submit_button.setToolTip("Enviar la solicitud de vacaciones")
        container_layout.addWidget(self.submit_button)
        self.submit_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.submit_button.clicked.connect(self.validate_and_submit)

        # Bottom spacer to separate content from lower border
        container_layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Add the container to the main layout
        main_layout.addWidget(container)

    def calculate_week(self):
        """
        Calculates the ISO week number for the vacation start date
        and updates the corresponding label.
        """
        date = self.vacation_start_input.date()
        week_num = date.weekNumber()[0]  # Returns (week, year)
        self.week_label.setText(f"Semana #: {week_num}")

    def on_national_id_changed(self, text: str) -> None:
        """
        Handles changes to the national ID input field.
        Validates both 9-digit national IDs and 12-digit DIMEX IDs.
        """
        # Check if the input is either 9 or 12 digits
        if len(text) not in (9, 12) or not text.isdigit():
            self.employee_info = None
            self.employee_name_input.clear()
            self.supervisor_input.clear()
            return

        # Fetch employee information based on the national ID
        employee_info = Employee.get_employee_by_national_id(text)
        if employee_info:
            # Populate the employee name
            full_name = f"{employee_info.first_name.strip()} {employee_info.last_name_1.strip()} {employee_info.last_name_2.strip()}"
            self.employee_name_input.setText(full_name)

            # Populate the supervisor's name
            supervisor_name = employee_info.supervisor.strip() if employee_info.supervisor else ""
            self.supervisor_input.setText(supervisor_name)

            # Store the employee information for later use
            self.employee_info = employee_info
        else:
            self.employee_info = None
            self.employee_name_input.clear()
            self.supervisor_input.clear()

    def validate_and_submit(self):
        """
        Validates the form and submits the vacation request.
        """
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
        
        # Check if the national ID corresponds to a valid employee
        if not self.employee_info or self.employee_info.national_id != national_id:
            show_warning_dialog(self, "Error", "La identificación ingresada no corresponde a un colaborador válido.")
            self.submit_button.setEnabled(True)
            return        
        
        # Name validation
        name = self.employee_name_input.text().strip()
        if not name or not all(c.isalpha() or c.isspace() for c in name):
            show_warning_dialog(self, "Error", "El nombre solo puede contener letras y espacios.")
            self.submit_button.setEnabled(True)
            return

        # Date validation and conversion
        request_date_qdate = self.request_date_input.date()
        start_date_qdate = self.vacation_start_input.date()
        end_date_qdate = self.vacation_end_input.date()

        request_date = date(
            request_date_qdate.year(),
            request_date_qdate.month(),
            request_date_qdate.day()
        )
        start_date = date(
            start_date_qdate.year(),
            start_date_qdate.month(),
            start_date_qdate.day()
        )
        end_date = date(
            end_date_qdate.year(),
            end_date_qdate.month(),
            end_date_qdate.day()
        )

        today = date.today()
        if start_date < today:
            show_warning_dialog(self, "Error", "No puede solicitar vacaciones para una fecha pasada.")
            self.submit_button.setEnabled(True)
            return

        if start_date > end_date:
            show_warning_dialog(self, "Error", "La fecha de inicio no puede ser posterior a la fecha final.")
            self.submit_button.setEnabled(True)
            return

        # Gather all required fields
        from logic.vacations_logic import VacationsLogic
        if not self.employee_info:
            show_warning_dialog(self, "Error", "No se pudo obtener la información del colaborador.")
            self.submit_button.setEnabled(True)
            return

        # Get supervisor's national ID using the full name
        supervisor_name = self.supervisor_input.text().strip()
        approved_by_id = None
        if supervisor_name:
            approved_by_id = Employee.get_national_id_by_full_name(supervisor_name)
            if not approved_by_id:
                show_warning_dialog(self, "Error", f"No se encontró la cédula del supervisor: {supervisor_name}.")
                self.submit_button.setEnabled(True)
                return

        national_id = self.employee_info.national_id
        total_days = len(VacationsLogic.get_business_days_in_range(start_date, end_date))
        status = "Pendiente"
        week_number = start_date.isocalendar()[1]

        # Call backend logic with all fields
        try:
            success, message = VacationsLogic.create_vacation_request(
                request_date,
                start_date,
                end_date,
                total_days,
                status,
                week_number,
                national_id,
                approved_by_id
            )
            if success:
                show_information_dialog(self, "Éxito", "Solicitud enviada correctamente.")
                self.notify_vacation_request(national_id, request_date, start_date, end_date)
                self.reset_form()
            else:
                show_warning_dialog(self, "Error", message)
        except Exception as e:
            logging.error(f"Error al crear la solicitud de vacaciones: {e}")
            show_critical_dialog(self, "Error crítico", "Ocurrió un error inesperado al procesar la solicitud.")

    def notify_vacation_request(self, national_id: str, request_date: date, start_date: date, end_date: date):
        """
        Notify relevant emails and the supervisor about a vacation request.
        """
        # Define the additional emails to notify
        additional_emails = ["ebarrantes@ewmfg.com", "ocastillo@ewmfg.com", "groman@ewmfg.com", "sbolivar@ewmfg.com"]

        # Fetch employee information
        employee_info = Employee.get_employee_by_national_id(national_id)
        if not employee_info:
            show_warning_dialog(self, "Error", f"No se encontró información del colaborador con cédula: {national_id}.")
            logging.warning(f"No employee found with National ID: {national_id}.")
            return

        # Fetch supervisor's national ID if a supervisor exists
        supervisor_id = None
        if employee_info.supervisor:
            supervisor_id = Employee.get_national_id_by_full_name(employee_info.supervisor)
            if not supervisor_id:
                show_warning_dialog(self, "Error", f"No se encontró la cédula del supervisor: {employee_info.supervisor}.")
                logging.warning(f"No national ID found for supervisor: {employee_info.supervisor}.")

        # Fetch recipients
        recipients = fetch_recipients(employee_info.national_id, supervisor_id, additional_emails) #type: ignore
        if not recipients:
            show_warning_dialog(self, "Error", "No se encontraron destinatarios para el correo.")
            logging.warning("No recipients found for the email.")
            return

        # Email details
        subject = "Solicitud Vacaciones"
        body = (
        f"Se le informa que el trabajador {employee_info.first_name.strip()} {employee_info.last_name_1.strip()} {employee_info.last_name_2.strip()} ha\n"
        f"solicitado una vacación desde el {start_date.strftime('%d/%m/%Y')} hasta el {end_date.strftime('%d/%m/%Y')}.\n\n"
        f"Por favor proceda a aprobar o denegar la solicitud.\n\n"
        )

        # Send the email
        if send_email(subject, body, recipients):
            show_information_dialog(self, "Éxito", "El correo de notificación se envió correctamente.")
            logging.info(f"Email sent successfully for vacation request by employee with National ID: {national_id}.")
        else:
            show_warning_dialog(self, "Error", "No se pudo enviar el correo de notificación.")
            logging.error(f"Failed to send email for vacation request by employee with National ID: {national_id}.")

    def reset_form(self):
        """
        Resets all form fields to their default values.
        """
        # Reset identification field
        if not self.national_id_input.isReadOnly():
            self.national_id_input.clear()

        # Reset full name
        self.employee_name_input.clear()

        # Reset start and end dates to the current date
        today = QDate.currentDate()
        self.vacation_start_input.setDate(today)
        self.vacation_end_input.setDate(today)

        # Reset approved by field
        self.supervisor_input.clear()

        # Reset week number to the current week
        self.calculate_week()