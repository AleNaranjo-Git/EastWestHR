from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QHeaderView, QSizePolicy, QComboBox, QLineEdit, QDateEdit, QScrollArea, QFrame, QTableWidgetItem, QGridLayout,
    QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, INPUT_STYLE, COMBOBOX_STYLE,
    FILTER_BUTTON_STYLE, CARD_STYLE, INFO_CARD_STYLE, 
    FILTER_TITLE_STYLE, CLEAR_FILTERS_STYLE, REJECT_BUTTON_STYLE, MESSAGE_BOX_STYLE
)
from logic.auth import get_current_user_national_id
from logic.unified_requests import get_unified_requests_by_supervisor, UnifiedRequest
from logic.email_service import send_email, fetch_recipients
from models.permit_request_model import PermitRequest
from models.permit_type_model import PermitType
from models.vacation_request_model import VacationRequest
from models.employee_model import Employee
from typing import List, Optional
from datetime import date
from utils.dialog_utils import show_warning_dialog, show_information_dialog
import logging

class PendingRequestPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {BACKGROUND}; color: {TEXT_COLOR};")
        self.unified_requests = []
        self.setup_ui()
        self.load_requests()

    def setup_ui(self):
        self.setMinimumSize(400, 300)
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # --- Title Section ---
        title = QLabel("Solicitudes Pendientes")
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # --- Filter Button Section ---
        filter_button_container = QHBoxLayout()
        self.filter_button = QPushButton(" Filtrar tabla")
        self.filter_button.setIcon(QIcon("resources/icons/filter.png"))
        self.filter_button.setStyleSheet(FILTER_BUTTON_STYLE)
        self.filter_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_button.setFixedWidth(150)
        filter_button_container.addWidget(self.filter_button)
        filter_button_container.addStretch()
        main_layout.addLayout(filter_button_container)

        # --- Filter Panel Section ---
        self.filter_frame = QFrame()
        self.filter_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.filter_frame.setStyleSheet(CARD_STYLE)
        self.filter_frame.setVisible(False)
        filter_layout = QVBoxLayout(self.filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(10)

        filter_header = QHBoxLayout()
        filter_title = QLabel("Filtrar registros")
        filter_title.setStyleSheet(FILTER_TITLE_STYLE)
        clear_filters_btn = QPushButton("Limpiar filtros")
        clear_filters_btn.setStyleSheet(CLEAR_FILTERS_STYLE)
        filter_header.addWidget(filter_title)
        filter_header.addStretch()
        filter_header.addWidget(clear_filters_btn)
        filter_layout.addLayout(filter_header)

        self.employee_filter = QLineEdit()
        self.employee_filter.setPlaceholderText("Identificación o Nombre")
        self.employee_filter.setStyleSheet(INPUT_STYLE)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Pendiente", "Aprobado", "Denegado"]) # type: ignore
        self.status_filter.setStyleSheet(COMBOBOX_STYLE)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todos", "Vacacion", "Permiso"]) # type: ignore
        self.type_filter.setStyleSheet(COMBOBOX_STYLE)

        self.permit_type_filter = QComboBox()
        permit_types = PermitType.get_all_active_permits()
        permit_type_names = [str(pt.permit_type_name) for pt in permit_types]
        self.permit_type_filter.addItems(["Todos"] + permit_type_names) # type: ignore
        self.permit_type_filter.setStyleSheet(COMBOBOX_STYLE)

        self.start_date_filter = QDateEdit()
        self.start_date_filter.setCalendarPopup(True)
        self.start_date_filter.setDisplayFormat("yyyy-MM-dd")
        self.start_date_filter.setDate(QDate(2000, 1, 1))

        self.end_date_filter = QDateEdit()
        self.end_date_filter.setCalendarPopup(True)
        self.end_date_filter.setDisplayFormat("yyyy-MM-dd")
        self.end_date_filter.setDate(QDate(2100, 12, 31))

        filter_grid = QGridLayout()
        filter_grid.setColumnStretch(1, 1)
        filter_grid.setColumnStretch(3, 1)

        filter_grid.addWidget(QLabel("Colaborador:"), 0, 0)
        filter_grid.addWidget(self.employee_filter, 0, 1)
        filter_grid.addWidget(QLabel("Estado:"), 0, 2)
        filter_grid.addWidget(self.status_filter, 0, 3)
        filter_grid.addWidget(QLabel("Tipo:"), 1, 0)
        filter_grid.addWidget(self.type_filter, 1, 1)
        filter_grid.addWidget(QLabel("Tipo de permiso:"), 1, 2)
        filter_grid.addWidget(self.permit_type_filter, 1, 3)
        filter_grid.addWidget(QLabel("Desde:"), 2, 0)
        filter_grid.addWidget(self.start_date_filter, 2, 1)
        filter_grid.addWidget(QLabel("Hasta:"), 2, 2)
        filter_grid.addWidget(self.end_date_filter, 2, 3)

        for row in range(filter_grid.rowCount()):
            for col in range(filter_grid.columnCount()):
                item = filter_grid.itemAtPosition(row, col)
                if item:
                    widget = item.widget()
                    if isinstance(widget, QLabel):
                        widget.setStyleSheet(LABEL_STYLE)

        apply_filter_btn = QPushButton("Aplicar filtros")
        apply_filter_btn.setStyleSheet(BUTTON_STYLE)
        apply_filter_btn.setFixedWidth(140)

        filter_layout.addLayout(filter_grid)
        filter_layout.addWidget(apply_filter_btn, 0, Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.filter_frame)
        main_layout.addSpacing(5)

        # --- Table Section ---
        table_scroll = QScrollArea()
        table_scroll.setWidgetResizable(True)
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels([ # type: ignore
            "Nombre solicitante", "Identificación", "Tipo", "Tipo de permiso", "Solicitada el", "Fecha inicio", "Fecha final",
            "Hora entrada", "Hora salida", "Cantidad de días", "Estado"
        ])
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setMinimumHeight(120)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table_layout.addWidget(self.table)
        table_scroll.setWidget(table_container)
        main_layout.addWidget(table_scroll, stretch=1)

        # --- Info Section ---
        info_card = QFrame()
        info_card.setFrameShape(QFrame.Shape.StyledPanel)
        info_card.setStyleSheet(INFO_CARD_STYLE)
        info_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        info_layout = QGridLayout(info_card)
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setHorizontalSpacing(24)
        info_layout.setVerticalSpacing(8)

        header = QLabel("Detalle de la solicitud seleccionada")
        header.setStyleSheet(FILTER_TITLE_STYLE)  
        info_layout.addWidget(header, 0, 0, 1, 4)

        def create_label_pair(title, row, col): # type: ignore
            label = QLabel(title) # type: ignore
            label.setStyleSheet(LABEL_STYLE) 
            
            value = QLabel("-")
            value.setStyleSheet(LABEL_STYLE)
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            
            info_layout.addWidget(label, row, col*2) # type: ignore
            info_layout.addWidget(value, row, col*2+1) # type: ignore
            return value

        self.name_label = create_label_pair("Nombre solicitante:", 1, 0)
        self.type_label_info = create_label_pair("Tipo:", 2, 0)
        self.requested_on_label = create_label_pair("Solicitada el:", 3, 0)
        self.start_date_label = create_label_pair("Fecha inicio:", 4, 0)
        self.entry_time_label = create_label_pair("Hora entrada:", 5, 0)
        self.days_label = create_label_pair("Cantidad de días:", 6, 0)

        self.national_id_label = create_label_pair("Identificación:", 1, 1)
        self.type_name_label = create_label_pair("Tipo de permiso:", 2, 1)
        self.status_label = create_label_pair("Estado:", 3, 1)
        self.end_date_label = create_label_pair("Fecha final:", 4, 1)
        self.exit_time_label = create_label_pair("Hora salida:", 5, 1)

        main_layout.addWidget(info_card)
        main_layout.addSpacing(10)

        # --- Approve/Reject Buttons Section ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.approve_button = QPushButton("Aprobar")
        self.approve_button.setStyleSheet(BUTTON_STYLE)
        self.approve_button.setFixedWidth(140)

        self.reject_button = QPushButton("Denegar")
        self.reject_button.setStyleSheet(REJECT_BUTTON_STYLE)
        self.reject_button.setFixedWidth(140)

        button_layout.addWidget(self.approve_button)
        button_layout.addWidget(self.reject_button)
        main_layout.addLayout(button_layout)

        # Connect table selection to info update
        self.table.selectionModel().selectionChanged.connect(self.update_info_from_selection)
        self.filter_button.clicked.connect(self.toggle_filter_panel)
        apply_filter_btn.clicked.connect(self.apply_filters)
        clear_filters_btn.clicked.connect(self.reset_filters)
        self.approve_button.clicked.connect(self.approve_selected)
        self.reject_button.clicked.connect(self.deny_selected)

    def load_requests(self):
        """
        Loads all requests for the current supervisor and sorts them by status.
        """
        supervisor_id = get_current_user_national_id()
        if supervisor_id:
            # Fetch all unified requests for the supervisor
            self.unified_requests = get_unified_requests_by_supervisor(supervisor_id)

            # Sort the requests by status: Pendiente -> Aprobado -> Denegado
            self.unified_requests.sort(key=lambda req: {
                "Pendiente": 1,
                "Aprobado": 2,
                "Denegado": 3
            }.get(req.status, 4))

            # Populate the table with the sorted requests
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
        """
        Applies filters to the requests and sorts the filtered results by status.
        """
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
        if start_date_filter != date(2000, 1, 1):
            filtered = [r for r in filtered if r.start_date >= start_date_filter]  # type: ignore
        if end_date_filter != date(2100, 12, 31):
            filtered = [r for r in filtered if r.end_date <= end_date_filter]  # type: ignore

        # Sort the filtered results by status
        filtered.sort(key=lambda req: {
            "Pendiente": 1,
            "Aprobado": 2,
            "Denegado": 3
        }.get(req.status, 4))

        # Populate the table with the sorted and filtered results
        self.populate_table(filtered)

        # Hide the filter panel after applying filters
        self.filter_frame.hide()
        self.filter_button.setText(" Filtrar tabla")
        self.repaint()  # Force UI update

    def reset_filters(self):
        self.employee_filter.clear()
        self.status_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.permit_type_filter.setCurrentIndex(0)
        self.start_date_filter.setDate(QDate(2000, 1, 1))
        self.end_date_filter.setDate(QDate(2100, 12, 31))
        self.populate_table(self.unified_requests)
        
        # Hide the filter panel after resetting
        self.filter_frame.hide()
        self.filter_button.setText(" Filtrar tabla")
        self.repaint()  # Force UI update

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
            self.national_id_label.setText("-")
            self.type_label_info.setText("-")
            self.type_name_label.setText("-")
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
            # Show confirmation dialog before proceeding
            confirmation = QMessageBox(self)
            confirmation.setWindowTitle("Confirmar solicitud")
            confirmation.setText("¿Está seguro/a que desea aprobar la solicitud?")
            confirmation.setStyleSheet(MESSAGE_BOX_STYLE)

            yes_button = confirmation.addButton("Sí", QMessageBox.ButtonRole.YesRole)
            confirmation.addButton("No", QMessageBox.ButtonRole.NoRole)
            confirmation.setDefaultButton(yes_button)

            confirmation.exec()
            if confirmation.clickedButton() != yes_button:
                return
            
            # Proceed with approval
            if req.type_ == "Permiso":
                PermitRequest.update_status(req.request_id, "Aprobado")
                self.notify_request(req, "Aprobación", "permiso", "aprobada")
            elif req.type_ == "Vacacion":
                VacationRequest.update_status(req.request_id, "Aprobado")
                self.notify_request(req, "Aprobación", "vacaciones", "aprobada")

            self.load_requests()  # Refresh table

    def deny_selected(self):
        req = self.get_selected_unified_request()
        if req:
           # Show confirmation dialog before proceeding
            confirmation = QMessageBox(self)
            confirmation.setWindowTitle("Confirmar solicitud")
            confirmation.setText("¿Está seguro/a que desea denegar la solicitud?")
            confirmation.setStyleSheet(MESSAGE_BOX_STYLE)

            yes_button = confirmation.addButton("Sí", QMessageBox.ButtonRole.YesRole)
            confirmation.addButton("No", QMessageBox.ButtonRole.NoRole)
            confirmation.setDefaultButton(yes_button)

            confirmation.exec()
            if confirmation.clickedButton() != yes_button:
                return
            # Proceed with denial
            if req.type_ == "Permiso":
                PermitRequest.update_status(req.request_id, "Denegado")
                self.notify_request(req, "Denegación", "permiso", "denegada")
            elif req.type_ == "Vacacion":
                VacationRequest.update_status(req.request_id, "Denegado")
                self.notify_request(req,"Denegación", "vacaciones", "denegada")

            self.load_requests()  # Refresh table
    
    def toggle_filter_panel(self):
        self.filter_frame.setVisible(not self.filter_frame.isVisible())
        if self.filter_frame.isVisible():
            self.filter_button.setText(" Ocultar filtros")
        else:
            self.filter_button.setText(" Filtrar tabla")

    def notify_request(self, req: "UnifiedRequest", action: str, requestType: str, solStatus: str) -> None:
        """
        Notify relevant emails and the supervisor about a vacation request.
        """
        # Define the additional emails to notify
        additional_emails = ["ebarrantes@ewmfg.com", "ocastillo@ewmfg.com", "groman@ewmfg.com", "sbolivar@ewmfg.com"]

        # Fetch employee information
        employee_info = Employee.get_employee_by_national_id(req.employee_national_id)
        if not employee_info:
            show_warning_dialog(self, "Error", f"No se encontró información del colaborador con cédula: {req.employee_national_id}.")
            logging.warning(f"No employee found with National ID: {req.employee_national_id}.")
            return

        # Fetch supervisor's national ID if a supervisor exists
        supervisor_id = None
        if employee_info.supervisor:
            supervisor_id = Employee.get_national_id_by_full_name(employee_info.supervisor)
            if not supervisor_id:
                show_warning_dialog(self, "Error", f"No se encontró la cédula del supervisor: {employee_info.supervisor}.")
                logging.warning(f"No national ID found for supervisor: {employee_info.supervisor}.")

        # Fetch recipients
        recipients = fetch_recipients(req.employee_national_id, supervisor_id, additional_emails) #type: ignore
        if not recipients:
            show_warning_dialog(self, "Error", "No se encontraron destinatarios para el correo.")
            logging.warning("No recipients found for the email.")
            return

        # Email details
        subject = f"{action} de {requestType}"
        body = (
            f"Se le informa que su solicitud de {requestType} para el día {req.start_date.strftime('%d/%m/%Y')}\n"
            f"fue {solStatus}.\n\n"
            f"Cualquier duda adicional por favor dirigirse con su jefatura inmediata.\n\n"
        )

        # Send the email
        if send_email(subject, body, recipients):
            show_information_dialog(self, "Éxito", f"El correo de notificación de {action.lower()} se envió correctamente.")
            logging.info(f"Email sent successfully for {action.lower()} request by employee with National ID: {req.employee_national_id}.")
        else:
            show_warning_dialog(self, "Error", f"No se pudo enviar el correo de notificación de {action.lower()}.")
            logging.error(f"Failed to send email for {action.lower()} request by employee with National ID: {req.employee_national_id}.")


    # Helper for QTableWidgetItem with alignment
def QLabelItem(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item
