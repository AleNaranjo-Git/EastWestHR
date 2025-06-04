from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout,
    QDateEdit, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QDate
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    INPUT_STYLE, BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, DATE_EDIT_STYLE
)
from logic.employee_logic import EmployeeLogic

class VacationsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.setup_ui()
        self.showMaximized()

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
        # Employee name
        employee_name_label = QLabel("Nombre del trabajador:")
        employee_name_label.setStyleSheet(LABEL_STYLE)
        self.employee_name_input = QLineEdit()
        self.employee_name_input.setPlaceholderText("Nombre del trabajador")
        self.employee_name_input.setStyleSheet(INPUT_STYLE)
        self.employee_name_input.setToolTip("Ingrese el nombre completo del trabajador")
        form.addRow(employee_name_label, self.employee_name_input)

        # National ID
        national_id_label = QLabel("Cédula:")
        national_id_label.setStyleSheet(LABEL_STYLE)
        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText("Ej: 123456789")
        self.national_id_input.setStyleSheet(INPUT_STYLE)
        self.national_id_input.setToolTip("Ingrese la cédula del trabajador")
        form.addRow(national_id_label, self.national_id_input)

        # Connect to search as user types
        self.national_id_input.textChanged.connect(self.on_national_id_changed)

        # Request date
        request_date_label = QLabel("Fecha de solicitud:")
        request_date_label.setStyleSheet(LABEL_STYLE)
        self.request_date_input = QDateEdit()
        self.request_date_input.setCalendarPopup(True)
        self.request_date_input.setDate(QDate.currentDate())
        self.request_date_input.setStyleSheet(DATE_EDIT_STYLE)
        self.request_date_input.setToolTip("Seleccione la fecha de solicitud")
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
        status_label = QLabel("Estado:")
        status_label.setStyleSheet(LABEL_STYLE)
        self.status_input = QLineEdit()
        self.status_input.setText("Pendiente")  # Default system value
        self.status_input.setStyleSheet(INPUT_STYLE)
        self.status_input.setToolTip("Estado de la solicitud")
        self.status_input.setReadOnly(True)  # Block user input
        self.status_input.setEnabled(False)  # Also disables focus/click
        form.addRow(status_label, self.status_input)

        # Supervisor approval
        supervisor_label = QLabel("Aprobado por:")
        supervisor_label.setStyleSheet(LABEL_STYLE)
        self.supervisor_input = QLineEdit()
        self.supervisor_input.setPlaceholderText("Nombre de quien aprueba")
        self.supervisor_input.setStyleSheet(INPUT_STYLE)
        self.supervisor_input.setToolTip("Nombre de la persona que aprueba")
        self.supervisor_input.setReadOnly(True)  # Block user input
        self.supervisor_input.setEnabled(False)  # Also disables focus/click
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
        if len(text) < 4:
            self.employee_name_input.clear()
            self.supervisor_input.clear()
            self.current_supervisor_id = None
            return
        employee_info = EmployeeLogic.get_employee_full_info_by_national_id(text)
        if employee_info:
            full_name = f"{employee_info['first_name']} {employee_info['last_name_1']} {employee_info['last_name_2']}"
            self.employee_name_input.setText(full_name)
            supervisor_name = employee_info['supervisor'] if employee_info['supervisor'] else ""
            self.supervisor_input.setText(supervisor_name)
            self.current_supervisor_id = employee_info.get('supervisor_id', None)
        else:
            self.employee_name_input.clear()
            self.supervisor_input.clear()
            self.current_supervisor_id = None
