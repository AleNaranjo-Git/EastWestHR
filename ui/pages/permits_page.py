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
from logic.employee_logic import EmployeeLogic
from logic.auth import Session
from logic.permits_logic import PermitsLogic
from models.permit_type_model import PermitType
from typing import List 


class PermitsPage(QWidget):
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
        employee_name_label = QLabel("Nombre del trabajador:")
        employee_name_label.setStyleSheet(LABEL_STYLE)
        self.employee_name_input = QLineEdit()
        self.employee_name_input.setPlaceholderText("Nombre del trabajador")
        self.employee_name_input.setStyleSheet(INPUT_STYLE)
        self.employee_name_input.setToolTip("Ingrese el nombre completo del trabajador")
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
        status_label = QLabel("Estado:")
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
        if len(text) != 9:
            return
        employee_info = EmployeeLogic.get_employee_full_info_by_national_id(text)
        if employee_info:
            full_name = f"{employee_info['first_name'].strip()} {employee_info['last_name_1'].strip()} {employee_info['last_name_2'].strip()}"
            self.employee_name_input.setText(full_name)
            supervisor_name = employee_info['supervisor'] if employee_info['supervisor'] else ""
            self.supervisor_input.setText(supervisor_name)
            self.current_supervisor_id = employee_info.get('supervisor_id', None)
            self.employee_info = employee_info

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
        reply = QMessageBox.question(
            self,
            "Confirmar solicitud",
            "¿Está seguro/a que toda la información introducida es correcta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # National ID validation
        national_id = self.national_id_input.text().strip()
        if not national_id.isdigit() or len(national_id) != 9:
            QMessageBox.warning(self, "Error", "La cédula debe contener exactamente 9 números.")
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
            QMessageBox.warning(self, "Error", "No puede solicitar un permiso para una fecha pasada.")
            return

        # Entry and exit time validation
        entry_time_text = self.entry_time_input.text().strip()
        exit_time_text = self.exit_time_input.text().strip()
        if not entry_time_text or not exit_time_text:
            QMessageBox.warning(self, "Error", "Debe ingresar las horas de ingreso y salida.")
            return

        try:
            entry_time = time.fromisoformat(entry_time_text)
            exit_time = time.fromisoformat(exit_time_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "El formato de las horas debe ser HH:mm.")
            return

        # Permit type validation
        permit_type_name = self.permit_type_combo.currentText()
        permit_type = PermitType.get_id_by_name(permit_type_name)
        if not permit_type:
            QMessageBox.warning(self, "Error", "El tipo de permiso seleccionado no es válido.")
            return

        # Gather all required fields
        request_date_qdate = self.request_date_input.date()
        request_date = date(
            request_date_qdate.year(),
            request_date_qdate.month(),
            request_date_qdate.day()
        )
        status = self.status_input.text().strip().lower()
        week_number = absence_date.isocalendar()[1]

        # Ensure approved_by_id is a string
        approved_by_id = str(self.current_supervisor_id) if self.current_supervisor_id else ""

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
            QMessageBox.information(self, "Éxito", "Solicitud de permiso enviada correctamente.")
        else:
            QMessageBox.warning(self, "Error", message)
