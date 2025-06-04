from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout,
    QComboBox, QDateEdit, QHBoxLayout, QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from resources.styles.colors import BACKGROUND, TEXT_COLOR
from resources.styles.components import (
    INPUT_STYLE, BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, DATE_EDIT_STYLE, COMBOBOX_STYLE, SEPARATOR_LINE_STYLE
)


class PermitsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.setup_ui()

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
        # Employee name
        employee_name_label = QLabel("Nombre del trabajador:")
        employee_name_label.setStyleSheet(LABEL_STYLE)
        self.employee_name_input = QLineEdit()
        self.employee_name_input.setPlaceholderText("Nombre del trabajador")
        self.employee_name_input.setStyleSheet(INPUT_STYLE)
        self.employee_name_input.setToolTip("Ingrese el nombre completo del trabajador")
        form.addRow(employee_name_label, self.employee_name_input)

        # Employee ID
        employee_id_label = QLabel("Cédula:")
        employee_id_label.setStyleSheet(LABEL_STYLE)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setPlaceholderText("Ej: 123456789")
        self.employee_id_input.setStyleSheet(INPUT_STYLE)
        self.employee_id_input.setToolTip("Ingrese la cédula del trabajador")
        form.addRow(employee_id_label, self.employee_id_input)

        # Request date
        request_date_label = QLabel("Fecha de solicitud:")
        request_date_label.setStyleSheet(LABEL_STYLE)
        self.request_date_input = QDateEdit()
        self.request_date_input.setCalendarPopup(True)
        self.request_date_input.setDate(QDate.currentDate())
        self.request_date_input.setStyleSheet(DATE_EDIT_STYLE)
        self.request_date_input.setToolTip("Seleccione la fecha de solicitud")
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
        self.permit_type_combo.addItems(list([ # type: ignore
            "Personal", "Médico", "Familiar", "Vacaciones", "Otro"
        ])) 
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
        self.status_input.setText("Pendiente")  # Default system value
        self.status_input.setStyleSheet(INPUT_STYLE)
        self.status_input.setToolTip("Estado de la solicitud")
        self.status_input.setReadOnly(True)  # Block user input
        self.status_input.setEnabled(False)  # Also disables focus/click
        form.addRow(status_label, self.status_input)

        # Approved by
        approved_by_label = QLabel("Aprobado por:")
        approved_by_label.setStyleSheet(LABEL_STYLE)
        self.approved_by_input = QLineEdit()
        self.approved_by_input.setPlaceholderText("Nombre de quien aprueba")
        self.approved_by_input.setStyleSheet(INPUT_STYLE)
        self.approved_by_input.setToolTip("Nombre de la persona que aprueba el permiso")
        self.approved_by_input.setReadOnly(True)  # Block user input
        self.approved_by_input.setEnabled(False)  # Also disables focus/click
        form.addRow(approved_by_label, self.approved_by_input)

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
