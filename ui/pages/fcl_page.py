# pages/flc_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout,
    QDateEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QDate
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    INPUT_STYLE, BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, DATE_EDIT_STYLE
)

class FCLPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.setup_ui()

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

        # Employee name
        name_label = QLabel("Nombre:")
        name_label.setStyleSheet(LABEL_STYLE)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del trabajador")
        self.name_input.setStyleSheet(INPUT_STYLE)
        self.name_input.setToolTip("Ingrese el nombre completo del trabajador")
        form.addRow(name_label, self.name_input)

        # Employee ID
        id_label = QLabel("Cédula:")
        id_label.setStyleSheet(LABEL_STYLE)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ej: 123456789")
        self.id_input.setStyleSheet(INPUT_STYLE)
        self.id_input.setToolTip("Ingrese la cédula del trabajador")
        form.addRow(id_label, self.id_input)

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
        self.submit_button = QPushButton("Solicitar FCL")
        self.submit_button.setStyleSheet(BUTTON_STYLE)
        self.submit_button.setToolTip("Solicitar FCL")
        container_layout.addWidget(self.submit_button)
        self.submit_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        main_layout.addWidget(container)