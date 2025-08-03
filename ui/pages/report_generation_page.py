from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QHeaderView, QSizePolicy, QComboBox, QLineEdit, QDateEdit, QScrollArea, QFrame, QTableWidgetItem, QGridLayout, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, INPUT_STYLE, COMBOBOX_STYLE,
    FILTER_BUTTON_STYLE, CARD_STYLE, 
    FILTER_TITLE_STYLE, CLEAR_FILTERS_STYLE
)
from logic.unified_requests import get_all_unified_requests_ordered, UnifiedRequest
from typing import Dict, List
from datetime import date
from logic.document_generation import generate_excel_report
from utils.dialog_utils import  show_warning_dialog, show_information_dialog

class ReportGenerationPage(QWidget):
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
        title = QLabel("Generación de Reportes")
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
        self.employee_filter.setPlaceholderText("Identificación o nombre")
        self.employee_filter.setStyleSheet(INPUT_STYLE)

        self.supervisor_filter = QLineEdit()
        self.supervisor_filter.setPlaceholderText("Nombre del Supervisor")
        self.supervisor_filter.setStyleSheet(INPUT_STYLE)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Pendiente", "Aprobado", "Denegado"]) # type: ignore
        self.status_filter.setStyleSheet(COMBOBOX_STYLE)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todos", "Vacacion", "Permiso"]) # type: ignore
        self.type_filter.setStyleSheet(COMBOBOX_STYLE)

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
        filter_grid.addWidget(QLabel("Supervisor:"), 0, 2)
        filter_grid.addWidget(self.supervisor_filter, 0, 3)
        filter_grid.addWidget(QLabel("Estado:"), 1, 0)
        filter_grid.addWidget(self.status_filter, 1, 1)
        filter_grid.addWidget(QLabel("Tipo:"), 1, 2)
        filter_grid.addWidget(self.type_filter, 1, 3)
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

        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels([ # type: ignore
            "Nombre solicitante", "Identificación", "Tipo", "Tipo de permiso", "Solicitada el", "Fecha inicio", "Fecha final",
            "Hora entrada", "Hora salida", "Cantidad de días", "Estado", "Nombre del Supervisor"
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

        # --- Generate Report Button Section ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.generate_report_button = QPushButton("Generar reporte en Excel")
        self.generate_report_button.setStyleSheet(BUTTON_STYLE)
        self.generate_report_button.setFixedWidth(400)

        button_layout.addWidget(self.generate_report_button)
        main_layout.addLayout(button_layout)

        # Connect table selection to info update
        self.filter_button.clicked.connect(self.toggle_filter_panel)
        apply_filter_btn.clicked.connect(self.apply_filters)
        clear_filters_btn.clicked.connect(self.reset_filters)
        self.generate_report_button.clicked.connect(self.export_table_to_excel)

    def load_requests(self):
        self.unified_requests = get_all_unified_requests_ordered()
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
            self.table.setItem(row, 11, QLabelItem(str(req.supervisor_name)))

    def apply_filters(self):
        filtered = self.unified_requests
        emp_filter = self.employee_filter.text().strip()
        supervisor_filter = self.supervisor_filter.text().strip()
        status_filter = self.status_filter.currentText()
        type_filter = self.type_filter.currentText()
        start_date_filter = self.start_date_filter.date().toPython()
        end_date_filter = self.end_date_filter.date().toPython()

        if emp_filter:
            filtered = [r for r in filtered if emp_filter in r.employee_name or emp_filter in r.employee_national_id]
        if supervisor_filter:
            filtered = [r for r in filtered if r.supervisor_name and supervisor_filter in r.supervisor_name]
        if status_filter != "Todos":
            filtered = [r for r in filtered if r.status.lower() == status_filter.lower()]
        if type_filter != "Todos":
            filtered = [r for r in filtered if r.type_.lower() == type_filter.lower()]
        # Only filter if user changed from default
        if start_date_filter != date(2000, 1, 1):
            filtered = [r for r in filtered if r.start_date >= start_date_filter]  # type: ignore
        if end_date_filter != date(2100, 12, 31):
            filtered = [r for r in filtered if r.end_date <= end_date_filter]  # type: ignore

        self.populate_table(filtered)

        self.filter_frame.hide()
        self.filter_button.setText(" Filtrar tabla")
        self.repaint()

    def reset_filters(self):
        self.employee_filter.clear()
        self.supervisor_filter.clear()
        self.status_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.start_date_filter.setDate(QDate(2000, 1, 1))
        self.end_date_filter.setDate(QDate(2100, 12, 31))
        self.populate_table(self.unified_requests)
        
        # Hide the filter panel after resetting
        self.filter_frame.hide()
        self.filter_button.setText(" Filtrar tabla")
        self.repaint()  # Force UI update

    def export_table_to_excel(self):
        # Prepare data from the current table view
        data: List[Dict[str, str]] = []  # Explicitly define the type of data
        for row in range(self.table.rowCount()):
            record: Dict[str, str] = {  # Explicitly define the type of record
                "type_": self.get_cell_text(row, 2),
                "permit_type_name": self.get_cell_text(row, 3),
                "employee_name": self.get_cell_text(row, 0),
                "employee_national_id": self.get_cell_text(row, 1),
                "request_date": self.get_cell_text(row, 4),
                "start_date": self.get_cell_text(row, 5),
                "end_date": self.get_cell_text(row, 6),
                "check_in_time": self.get_cell_text(row, 7),
                "check_out_time": self.get_cell_text(row, 8),
                "total_days": self.get_cell_text(row, 9),
                "status": self.get_cell_text(row, 10),
                "supervisor_name": self.get_cell_text(row, 11),
            }
            data.append(record)

        # Open a file dialog for the user to select the save location
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte en Excel",
            "Reporte.xlsx",
            "Excel Files (*.xlsx)"
        )

        # If the user cancels the dialog, do nothing
        if not output_path:
            return

        # Generate the Excel report
        if generate_excel_report(output_path, data):
            show_information_dialog(self, "Éxito", f"Reporte de excel generado satisfactoriamente: {output_path}")
        else:
            show_warning_dialog(self, "Error", "No se pudo generar el reporte de Excel.")

    def toggle_filter_panel(self):
        self.filter_frame.setVisible(not self.filter_frame.isVisible())
        if self.filter_frame.isVisible():
            self.filter_button.setText(" Ocultar filtros")
        else:
            self.filter_button.setText(" Filtrar tabla")

    def get_cell_text(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item is not None else "-"

# Helper for QTableWidgetItem with alignment
def QLabelItem(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item
