# pages/aprobar_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QHeaderView, QGroupBox, QFormLayout, QSizePolicy, QComboBox, QLineEdit, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, INPUT_STYLE, COMBOBOX_STYLE
)
from logic.auth import get_current_user_national_id
from logic.unified_requests import get_unified_requests_by_supervisor, UnifiedRequest
from models.permit_request_model import PermitRequest
from models.permit_type_model import PermitType
from models.vacation_request_model import VacationRequest
from typing import List, Optional
from datetime import date

class PendingRequestPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.unified_requests = []
        self.setup_ui()
        self.load_requests()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(80, 40, 80, 40)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 30, 40, 30)
        # Allow the container to expand vertically
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Title
        title = QLabel("Solicitudes Pendientes")
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

        # Type filter
        type_label = QLabel("Tipo:")
        type_label.setStyleSheet(LABEL_STYLE)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todos", "Vacacion", "Permiso"])  # type: ignore
        self.type_filter.setStyleSheet(COMBOBOX_STYLE)
        self.type_filter.setFixedWidth(120)
        filter_bar.addWidget(type_label)
        filter_bar.addWidget(self.type_filter)
        
        # type of permit filter
        permit_type_label = QLabel("Tipo de permiso:")
        permit_type_label.setStyleSheet(LABEL_STYLE)
        self.permit_type_filter = QComboBox()
        permit_types = PermitType.get_all_active_permits()
        permit_type_names: List[str] = [str(pt.permit_type_name) for pt in permit_types]
        self.permit_type_filter.addItems(["Todos"] + permit_type_names)  # type: ignore
        self.permit_type_filter.setStyleSheet(COMBOBOX_STYLE)
        self.permit_type_filter.setFixedWidth(240)
        filter_bar.addWidget(permit_type_label)
        filter_bar.addWidget(self.permit_type_filter)

        # Start date filter
        start_date_label = QLabel("Fecha inicio desde:")
        start_date_label.setStyleSheet(LABEL_STYLE)
        self.start_date_filter = QDateEdit()
        self.start_date_filter.setCalendarPopup(True)
        self.start_date_filter.setDisplayFormat("yyyy-MM-dd")
        self.start_date_filter.setDate(QDate(2000, 1, 1))
        filter_bar.addWidget(start_date_label)
        filter_bar.addWidget(self.start_date_filter)

        # End date filter
        end_date_label = QLabel("Fecha final hasta:")
        end_date_label.setStyleSheet(LABEL_STYLE)
        self.end_date_filter = QDateEdit()
        self.end_date_filter.setCalendarPopup(True)
        self.end_date_filter.setDisplayFormat("yyyy-MM-dd")
        self.end_date_filter.setDate(QDate(2100, 12, 31))
        filter_bar.addWidget(end_date_label)
        filter_bar.addWidget(self.end_date_filter)

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
        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels([ # type: ignore
            "Nombre solicitante", "Cédula Empleado", "Tipo", "Tipo de permiso", "Solicitada el", "Fecha inicio", "Fecha final",
            "Hora entrada", "Hora salida", "Cantidad de días", "Estado"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setMinimumHeight(400)
        container_layout.addWidget(self.table)

        # Info group (shows details of selected request)
        info_group = QGroupBox("Detalle de la solicitud seleccionada")
        info_layout = QFormLayout()
        info_group.setLayout(info_layout)
        info_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.name_label = QLabel("-")
        self.name_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Nombre solicitante:", self.name_label)
        self.national_id_label = QLabel("-")
        self.national_id_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Cédula Empleado:", self.national_id_label)
        self.type_label_info = QLabel("-")
        self.type_label_info.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Tipo:", self.type_label_info)
        self.type_name_label = QLabel("-")
        self.type_name_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Tipo de permiso:", self.type_name_label)
        self.requested_on_label = QLabel("-")
        self.requested_on_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Solicitada el:", self.requested_on_label)
        self.start_date_label = QLabel("-")
        self.start_date_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Fecha inicio:", self.start_date_label)
        self.end_date_label = QLabel("-")
        self.end_date_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Fecha final:", self.end_date_label)
        self.entry_time_label = QLabel("-")
        self.entry_time_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Hora entrada:", self.entry_time_label)
        self.exit_time_label = QLabel("-")
        self.exit_time_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Hora salida:", self.exit_time_label)
        self.days_label = QLabel("-")
        self.days_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Cantidad de días:", self.days_label)
        self.status_label = QLabel("-")
        self.status_label.setStyleSheet(LABEL_STYLE)
        info_layout.addRow("Estado:", self.status_label)

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

        # Connect filter buttons
        self.filter_button.clicked.connect(self.apply_filters)
        self.clear_filters_button.clicked.connect(self.reset_filters)

        # Connect approve/reject buttons
        self.approve_button.clicked.connect(self.approve_selected)
        self.reject_button.clicked.connect(self.deny_selected)

    def load_requests(self):
        supervisor_id = get_current_user_national_id()
        if supervisor_id:
            self.unified_requests = get_unified_requests_by_supervisor(supervisor_id)
            self.populate_table(self.unified_requests)

    def populate_table(self, requests: List["UnifiedRequest"]) -> None:
        self.displayed_requests = requests
        self.table.setRowCount(0)
        for req in requests:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QLabelItem(str(req.employee_name)))
            self.table.setItem(row, 1, QLabelItem(str(req.employee_national_id)))
            self.table.setItem(row, 2, QLabelItem(str(req.type_)))
            self.table.setItem(row, 3, QLabelItem(str(req.permit_type_name)))
            self.table.setItem(row, 4, QLabelItem(str(req.request_date)))
            self.table.setItem(row, 5, QLabelItem(str(req.start_date)))
            self.table.setItem(row, 6, QLabelItem(str(req.end_date)))
            self.table.setItem(row, 7, QLabelItem(str(req.check_in_time)))
            self.table.setItem(row, 8, QLabelItem(str(req.check_out_time)))
            self.table.setItem(row, 9, QLabelItem(str(req.total_days)))
            self.table.setItem(row, 10, QLabelItem(str(req.status)))
            
    def get_selected_unified_request(self) -> Optional["UnifiedRequest"]:
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None
        return self.displayed_requests[selected_row]

    def apply_filters(self):
        filtered = self.unified_requests
        emp_filter = self.employee_filter.text().strip()
        status_filter = self.status_filter.currentText()
        type_filter = self.type_filter.currentText()
        permit_type_filter = self.permit_type_filter.currentText()
        start_date_filter = self.start_date_filter.date().toPython()
        end_date_filter = self.end_date_filter.date().toPython()

        if emp_filter:
            filtered = [r for r in filtered if emp_filter in r.employee_name or emp_filter in r.employee_national_id]
        if status_filter != "Todos":
            filtered = [r for r in filtered if r.status.lower() == status_filter.lower()]
        if type_filter != "Todos":
            filtered = [r for r in filtered if r.type_.lower() == type_filter.lower()]
        if permit_type_filter != "Todos":
            filtered = [r for r in filtered if r.permit_type_name.lower() == permit_type_filter.lower()]
        # Only filter if user changed from default
        if start_date_filter != date(2000, 1, 1):
            filtered = [r for r in filtered if r.start_date >= start_date_filter] # type: ignore
        if end_date_filter != date(2100, 12, 31):
            filtered = [r for r in filtered if r.end_date <= end_date_filter] # type: ignore

        self.populate_table(filtered)

    def reset_filters(self):
        self.employee_filter.clear()
        self.status_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.permit_type_filter.setCurrentIndex(0)
        self.start_date_filter.setDate(QDate(2000, 1, 1))
        self.end_date_filter.setDate(QDate(2100, 12, 31))
        self.populate_table(self.unified_requests)

    def update_info_from_selection(self):
        selected = self.table.currentRow()
        def safe_text(col: int) -> str:
            item = self.table.item(selected, col)
            return item.text() if item is not None else "-"
        if selected >= 0:
            self.name_label.setText(safe_text(0))
            self.national_id_label.setText(safe_text(1))
            self.type_label_info.setText(safe_text(2))
            self.type_name_label.setText(safe_text(3))
            self.requested_on_label.setText(safe_text(4))
            self.start_date_label.setText(safe_text(5))
            self.end_date_label.setText(safe_text(6))
            self.entry_time_label.setText(safe_text(7))
            self.exit_time_label.setText(safe_text(8))
            self.days_label.setText(safe_text(9))
            self.status_label.setText(safe_text(10))
        else:
            self.name_label.setText("-")
            self.national_id_label = QLabel("-")
            self.type_label_info.setText("-")
            self.requested_on_label.setText("-")
            self.start_date_label.setText("-")
            self.end_date_label.setText("-")
            self.entry_time_label.setText("-")
            self.exit_time_label.setText("-")
            self.days_label.setText("-")
            self.status_label.setText("-")
        selected_request = self.get_selected_unified_request()
        if selected_request:
            # Disable buttons if already approved or denied
            if selected_request.status in ("Aprobado", "Denegado"):
                self.approve_button.setEnabled(False)
                self.reject_button.setEnabled(False)
            else:
                self.approve_button.setEnabled(True)
                self.reject_button.setEnabled(True)
        else:
            # No selection, disable buttons
            self.approve_button.setEnabled(False)
            self.reject_button.setEnabled(False)

    def approve_selected(self):
        req = self.get_selected_unified_request()
        if req:
            if req.type_ == "Permiso":
                PermitRequest.update_status(req.request_id, "Aprobado")
            elif req.type_ == "Vacacion":
                VacationRequest.update_status(req.request_id, "Aprobado")
            self.load_requests()  # Refresh table

    def deny_selected(self):
        req = self.get_selected_unified_request()
        if req:
            if req.type_ == "Permiso":
                PermitRequest.update_status(req.request_id, "Denegado")
            elif req.type_ == "Vacacion":
                VacationRequest.update_status(req.request_id, "Denegado")
            self.load_requests()  # Refresh table

# Helper for QTableWidgetItem with alignment
from PySide6.QtWidgets import QTableWidgetItem
def QLabelItem(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item
