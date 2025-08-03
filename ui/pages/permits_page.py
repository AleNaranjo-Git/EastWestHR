from datetime import date, time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout,
    QComboBox, QDateEdit, QHBoxLayout, QFrame, QSizePolicy, QSpacerItem, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from resources.styles.colors import BACKGROUND, TEXT_COLOR
from resources.styles.components import (
    INPUT_STYLE, BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, DATE_EDIT_STYLE, COMBOBOX_STYLE, SEPARATOR_LINE_STYLE
)
from models.employee_model import Employee
from logic.auth import Session
from logic.permits_logic import PermitsLogic
from models.permit_type_model import PermitType
from logic.email_service import send_email, fetch_recipients
from typing import List 
import logging
from resources.styles.components import MESSAGE_BOX_STYLE
from utils.dialog_utils import show_information_dialog, show_warning_dialog, show_critical_dialog


class PermitsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.setup_ui()

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
        title = QLabel("Solicitar Permiso")
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

        # Absence date
        absence_date_label = QLabel("Fecha de ausencia:")
        absence_date_label.setStyleSheet(LABEL_STYLE)
        self.absence_date_input = QDateEdit()
        self.absence_date_input.setCalendarPopup(True)
        self.absence_date_input.setDate(QDate.currentDate())
        self.absence_date_input.setStyleSheet(DATE_EDIT_STYLE)
        self.absence_date_input.setToolTip("Seleccione la fecha de ausencia")
        form.addRow(absence_date_label, self.absence_date_input)
        self.absence_date_input.dateChanged.connect(self.calculate_week)

        # Permit type
        permit_type_label = QLabel("Tipo de permiso:")
        permit_type_label.setStyleSheet(LABEL_STYLE)
        self.permit_type_combo = QComboBox()
        permit_types = PermitType.get_all_active_permits()
        permit_type_names: List[str] = [str(pt.permit_type_name) for pt in permit_types]
        self.permit_type_combo.addItems(permit_type_names) # type: ignore
        self.permit_type_combo.setStyleSheet(COMBOBOX_STYLE)
        self.permit_type_combo.setToolTip("Seleccione el tipo de permiso")
        form.addRow(permit_type_label, self.permit_type_combo)

        # Visual separator with line and text
        separator_widget = QWidget()
        sep_layout = QHBoxLayout(separator_widget)
        sep_layout.setContentsMargins(0, 30, 0, 10)

        line_left = QFrame()
        line_left.setStyleSheet(SEPARATOR_LINE_STYLE)

        sep_label = QLabel("En caso de ser necesario, especificar:")
        sep_label.setStyleSheet(LABEL_STYLE)
        sep_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line_right = QFrame()
        line_right.setStyleSheet(SEPARATOR_LINE_STYLE)

        sep_layout.addWidget(line_left)
        sep_layout.addWidget(sep_label)
        sep_layout.addWidget(line_right)
        form.addRow(separator_widget)

        # Time validator for 24h format (HH:mm)
        time_regex = QRegularExpression(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
        time_validator = QRegularExpressionValidator(time_regex)

        # Entry time (QLineEdit with auto-insert ':')
        entry_time_label = QLabel("Hora de ingreso:")
        entry_time_label.setStyleSheet(LABEL_STYLE)
        self.entry_time_input = QLineEdit()
        self.entry_time_input.setPlaceholderText("HH:mm")
        self.entry_time_input.setMaxLength(5)
        self.entry_time_input.setValidator(time_validator)
        self.entry_time_input.setStyleSheet(INPUT_STYLE)
        self.entry_time_input.setToolTip("Ingrese la hora de ingreso (formato 24h)")
        form.addRow(entry_time_label, self.entry_time_input)
        self.entry_time_input.textChanged.connect(self.auto_insert_colon_entry)

        # Exit time (QLineEdit with auto-insert ':')
        exit_time_label = QLabel("Hora de salida:")
        exit_time_label.setStyleSheet(LABEL_STYLE)
        self.exit_time_input = QLineEdit()
        self.exit_time_input.setPlaceholderText("HH:mm")
        self.exit_time_input.setMaxLength(5)
        self.exit_time_input.setValidator(time_validator)
        self.exit_time_input.setStyleSheet(INPUT_STYLE)
        self.exit_time_input.setToolTip("Ingrese la hora de salida (formato 24h)")
        form.addRow(exit_time_label, self.exit_time_input)
        self.exit_time_input.textChanged.connect(self.auto_insert_colon_exit)

        # Status (system default, read-only)
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
        self.supervisor_input.setToolTip("Nombre de la persona que aprueba el permiso")
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
        self.submit_button = QPushButton("Solicitar Permiso")
        self.submit_button.setStyleSheet(BUTTON_STYLE)
        self.submit_button.setToolTip("Enviar la solicitud de permiso")
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
        Calculates the ISO week number for the absence date
        and updates the corresponding label.
        """
        date = self.absence_date_input.date()
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

    def auto_insert_colon_entry(self, text: str) -> None:
        """
        Automatically inserts ':' after the first two digits in entry time.
        """
        if len(text) == 2 and not text.endswith(":"):
            self.entry_time_input.setText(text + ":")
            self.entry_time_input.setCursorPosition(3)

    def auto_insert_colon_exit(self, text: str) -> None:
        """
        Automatically inserts ':' after the first two digits in exit time.
        """
        if len(text) == 2 and not text.endswith(":"):
            self.exit_time_input.setText(text + ":")
            self.exit_time_input.setCursorPosition(3)

    def validate_and_submit(self):
        """
        Validates the form inputs and submits the permit request.
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

        # Absence date validation
        absence_date_qdate = self.absence_date_input.date()
        absence_date = date(
            absence_date_qdate.year(),
            absence_date_qdate.month(),
            absence_date_qdate.day()
        )
        today = date.today()
        if absence_date < today:
            show_warning_dialog(self, "Error", "No puede solicitar un permiso para una fecha pasada.")
            return

        # Entry and exit time validation
        entry_time_text = self.entry_time_input.text().strip()
        exit_time_text = self.exit_time_input.text().strip()
        if not entry_time_text or not exit_time_text:
            show_warning_dialog(self, "Error", "Debe ingresar las horas de ingreso y salida.")
            return

        try:
            entry_time = time.fromisoformat(entry_time_text)
            exit_time = time.fromisoformat(exit_time_text)
        except ValueError:
            show_warning_dialog(self, "Error", "El formato de las horas debe ser HH:mm.")
            return

        # Permit type validation
        permit_type_name = self.permit_type_combo.currentText()
        permit_type = PermitType.get_id_by_name(permit_type_name)
        if not permit_type:
            show_warning_dialog(self, "Error", "El tipo de permiso seleccionado no es válido.")
            return

        # Gather all required fields
        request_date_qdate = self.request_date_input.date()
        request_date = date(
            request_date_qdate.year(),
            request_date_qdate.month(),
            request_date_qdate.day()
        )
        status = "Pendiente"
        week_number = absence_date.isocalendar()[1]

        # Get supervisor's national ID using the full name
        supervisor_name = self.supervisor_input.text().strip()
        approved_by_id = None
        if supervisor_name:
            approved_by_id = Employee.get_national_id_by_full_name(supervisor_name)
            if not approved_by_id:
                show_warning_dialog(self, "Error", f"No se encontró la cédula del supervisor: {supervisor_name}.")
                return

        # Ensure approved_by_id is a string
        approved_by_id = approved_by_id or ""

        try:
             # Call backend logic with all fields
            success, message = PermitsLogic.create_permit_request(
                request_date,
                absence_date,
                entry_time,
                exit_time,
                status,
                week_number,
                national_id,
                permit_type,
                approved_by_id
            )
            if success:
                show_information_dialog(self, "Éxito", "Solicitud de permiso enviada correctamente.")
                self.notify_permit_request(national_id, request_date, absence_date, permit_type_name)
                self.reset_form()
            else:
                show_warning_dialog(self, "Error", message)
        except Exception as e:
            logging.error(f"Error al crear la solicitud de permiso: {e}")
            show_critical_dialog(self, "Error crítico", "Ocurrió un error inesperado al procesar la solicitud.")
       
            
    def notify_permit_request(self, national_id: str, request_date: date, absence_date: date, permit_type_name: str):
        """
        Notify relevant departments and the supervisor about a vacation request.
        """
        # Define the departments to notify
        departments = ["TestEmail", "AnotherDepartment"]

        # Fetch employee information
        employee_info = Employee.get_employee_by_national_id(national_id)
        if not employee_info:
            show_warning_dialog(self, "Error", f"No se encontró información del colabolador con cédula: {national_id}.")
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
        recipients = fetch_recipients(employee_info.national_id, supervisor_id, departments)  # type: ignore
        if not recipients:
            show_warning_dialog(self, "Error", "No se encontraron destinatarios para el correo.")
            logging.warning("No recipients found for the email.")
            return

        # Email details
        subject = "Solicitud de Permiso"
        body = (
            f"Por la presente, se informa que el colaborador {employee_info.first_name} {employee_info.last_name_1} "
            f"({employee_info.national_id}) ha realizado una solicitud de permiso con los siguientes detalles:\n\n"
            f"Fecha de solicitud: {request_date.strftime('%d/%m/%Y')}\n"
            f"Fecha de ausencia: {absence_date.strftime('%d/%m/%Y')}\n"
            f"Tipo de permiso: {permit_type_name}"
        )

        # Send the email
        if send_email(subject, body, recipients):
            show_information_dialog(self, "Éxito", "El correo de notificación se envió correctamente.")
            logging.info(f"Email sent successfully for permit request by employee with National ID: {national_id}.")
        else:
            show_warning_dialog(self, "Error", "No se pudo enviar el correo de notificación.")
            logging.error(f"Failed to send email for permit request by employee with National ID: {national_id}.")
    
    def reset_form(self):
        """
        Resets all form fields to their default values.
        """
        # Reset National ID (if editable)
        if not self.national_id_input.isReadOnly():
            self.national_id_input.clear()

        # Reset employee name
        self.employee_name_input.clear()

        # Reset absence date to today
        self.absence_date_input.setDate(QDate.currentDate())

        # Reset permit type to the first option
        if self.permit_type_combo.count() > 0:
            self.permit_type_combo.setCurrentIndex(0)

        # Reset entry and exit times
        self.entry_time_input.clear()
        self.exit_time_input.clear()

        # Reset supervisor name
        self.supervisor_input.clear()

        # Reset week number to the current week
        self.calculate_week()
