# pages/aprobar_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QHeaderView, QGroupBox, QFormLayout, QSizePolicy, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, INPUT_STYLE, COMBOBOX_STYLE
)

class PendingRequestPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(80, 40, 80, 40)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 30, 40, 30)
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        # Title
        title = QLabel("Solicitudes de Vacaciones Pendientes")
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)

        # --- Filter bar ---
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)

        # Employee filter
        employee_label = QLabel("Empleado:")
        employee_label.setStyleSheet(LABEL_STYLE)
        self.employee_filter = QLineEdit()
        self.employee_filter.setPlaceholderText("Cédula: ej 123456789")
        self.employee_filter.setStyleSheet(INPUT_STYLE)
        self.employee_filter.setFixedWidth(180)
        filter_bar.addWidget(employee_label)
        filter_bar.addWidget(self.employee_filter)

        # Status filter
        status_label = QLabel("Estado:")
        status_label.setStyleSheet(LABEL_STYLE)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Pendiente", "Aprobado", "Denegado"]) # type: ignore
        self.status_filter.setStyleSheet(COMBOBOX_STYLE)
        self.status_filter.setFixedWidth(120)
        filter_bar.addWidget(status_label)
        filter_bar.addWidget(self.status_filter)

        # Filter button
        self.filter_button = QPushButton("Filtrar")
        self.filter_button.setStyleSheet(BUTTON_STYLE)
        self.filter_button.setMinimumWidth(120)
        filter_bar.addWidget(self.filter_button)

        # Clear filters button
        self.clear_filters_button = QPushButton("Limpiar filtros")
        self.clear_filters_button.setStyleSheet(BUTTON_STYLE)
        self.clear_filters_button.setMinimumWidth(120)
        filter_bar.addWidget(self.clear_filters_button)

        filter_bar.addStretch()
        container_layout.addLayout(filter_bar)

        # Table for pending requests
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([ # type: ignore
            "Nombre solicitante", "Solicitada el", "Fecha inicio", "Fecha final",
            "Cantidad de días", "Estado", "Número de semana"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        container_layout.addWidget(self.table)

        # Info group (shows details of selected request)
        info_group = QGroupBox("Detalle de la solicitud seleccionada")
        info_layout = QFormLayout()
        info_group.setLayout(info_layout)
        info_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.name_label = QLabel("-")
        self.name_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Nombre solicitante:", self.name_label)
        self.requested_on_label = QLabel("-")
        self.requested_on_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Solicitada el:", self.requested_on_label)
        self.start_date_label = QLabel("-")
        self.start_date_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Fecha inicio:", self.start_date_label)
        self.end_date_label = QLabel("-")
        self.end_date_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Fecha final:", self.end_date_label)
        self.days_label = QLabel("-")
        self.days_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Cantidad de días:", self.days_label)
        self.status_label = QLabel("-")
        self.status_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Estado:", self.status_label)
        self.week_label = QLabel("-")
        self.week_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Número de semana:", self.week_label)

        container_layout.addWidget(info_group)

        # Approve/Reject buttons
        button_layout = QHBoxLayout()
        self.approve_button = QPushButton("Aprobar")
        self.approve_button.setStyleSheet(BUTTON_STYLE)
        self.reject_button = QPushButton("Denegar")
        self.reject_button.setStyleSheet(BUTTON_STYLE)
        button_layout.addWidget(self.approve_button)
        button_layout.addWidget(self.reject_button)
        container_layout.addLayout(button_layout)

        main_layout.addWidget(container)

        # Connect table selection to info update
        self.table.selectionModel().selectionChanged.connect(self.update_info_from_selection)

        # Connect checkbox to show/hide date range
        self.clear_filters_button.clicked.connect(self.reset_filters)

    def update_info_from_selection(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.name_label.setText(self.table.item(selected, 0).text() if self.table.item(selected, 0) else "-") # type: ignore
            self.requested_on_label.setText(self.table.item(selected, 1).text() if self.table.item(selected, 1) else "-") # type: ignore
            self.start_date_label.setText(self.table.item(selected, 2).text() if self.table.item(selected, 2) else "-") # type: ignore
            self.end_date_label.setText(self.table.item(selected, 3).text() if self.table.item(selected, 3) else "-") # type: ignore
            self.days_label.setText(self.table.item(selected, 4).text() if self.table.item(selected, 4) else "-") # type: ignore
            self.status_label.setText(self.table.item(selected, 5).text() if self.table.item(selected, 5) else "-") # type: ignore
            self.week_label.setText(self.table.item(selected, 6).text() if self.table.item(selected, 6) else "-") # type: ignore
        else:
            self.name_label.setText("-")
            self.requested_on_label.setText("-")
            self.start_date_label.setText("-")
            self.end_date_label.setText("-")
            self.days_label.setText("-")
            self.status_label.setText("-")
            self.week_label.setText("-")

    def reset_filters(self):
        self.employee_filter.clear()
        self.status_filter.setCurrentIndex(0)
