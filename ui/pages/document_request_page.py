from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QHeaderView, QTableWidgetItem, QLineEdit, QScrollArea, QFrame, QGridLayout, QDateEdit, QComboBox, QSizePolicy,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
from resources.styles.colors import TEXT_COLOR, BACKGROUND
from resources.styles.components import (
    BUTTON_STYLE, TITLE_STYLE, LABEL_STYLE, INPUT_STYLE, CARD_STYLE, INFO_CARD_STYLE,
    FILTER_TITLE_STYLE, FILTER_BUTTON_STYLE, COMBOBOX_STYLE, CLEAR_FILTERS_STYLE
)
from logic.unified_document_request import UnifiedDocumentRequest
from models.fcl_model import FCL
from models.salary_certificate_model import SalaryCertificate
from logic.document_generation import generate_salary_certificate, generate_fcl
from models.employee_model import Employee
from typing import List, Dict
from datetime import date

class DocumentRequestPage(QWidget):
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
        title = QLabel("Solicitudes de Documentos")
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
        self.employee_filter.setPlaceholderText("Cédula o nombre")
        self.employee_filter.setStyleSheet(INPUT_STYLE)

        self.document_generated_filter = QComboBox()
        self.document_generated_filter.addItems(["Todos", "Documento no generado", "Documento generado"])  # type: ignore
        self.document_generated_filter.setStyleSheet(COMBOBOX_STYLE)

        self.start_date_filter = QDateEdit()
        self.start_date_filter.setCalendarPopup(True)
        self.start_date_filter.setDisplayFormat("yyyy-MM-dd")
        self.start_date_filter.setDate(QDate(2000, 1, 1))

        self.end_date_filter = QDateEdit()
        self.end_date_filter.setCalendarPopup(True)
        self.end_date_filter.setDisplayFormat("yyyy-MM-dd")
        self.end_date_filter.setDate(QDate(2100, 12, 31))

        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todos", "Constancia Salarial", "FCL"])
        self.type_filter.setStyleSheet(COMBOBOX_STYLE)

        filter_grid = QGridLayout()
        filter_grid.setColumnStretch(1, 1)
        filter_grid.setColumnStretch(3, 1)

        filter_grid.addWidget(QLabel("Empleado:"), 0, 0)
        filter_grid.addWidget(self.employee_filter, 0, 1)
        filter_grid.addWidget(QLabel("Estado documento:"), 0, 2)
        filter_grid.addWidget(self.document_generated_filter, 0, 3)
        filter_grid.addWidget(QLabel("Desde:"), 1, 0)
        filter_grid.addWidget(self.start_date_filter, 1, 1)
        filter_grid.addWidget(QLabel("Hasta:"), 1, 2)
        filter_grid.addWidget(self.end_date_filter, 1, 3)
        filter_grid.addWidget(QLabel("Tipo:"), 2, 0)
        filter_grid.addWidget(self.type_filter, 2, 1)

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

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Nombre solicitante", "Cédula Empleado", "Tipo", "Fecha Máxima", "Estado documento"
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
            
            info_layout.addWidget(label, row, col * 2) # type: ignore
            info_layout.addWidget(value, row, col * 2 + 1) # type: ignore
            return value

        self.name_label = create_label_pair("Nombre solicitante:", 1, 0)
        self.national_id_label = create_label_pair("Cédula Empleado:", 2, 0)
        self.type_label = create_label_pair("Tipo:", 3, 0)
        self.requested_on_label = create_label_pair("Solicitada el:", 4, 0)
        self.document_generated_label = create_label_pair("Estado documento:", 5, 0)

        main_layout.addWidget(info_card)
        main_layout.addSpacing(10)

        # Connect table selection to info update
        self.table.selectionModel().selectionChanged.connect(self.update_info_from_selection)
        self.filter_button.clicked.connect(self.toggle_filter_panel)
        apply_filter_btn.clicked.connect(self.apply_filters)
        clear_filters_btn.clicked.connect(self.reset_filters)

        # Add buttons for generating documents
        self.generate_fcl_button = QPushButton("Generar FCL")
        self.generate_fcl_button.setStyleSheet(BUTTON_STYLE)
        self.generate_fcl_button.setFixedWidth(400)

        self.generate_salary_certificate_button = QPushButton("Generar Constancia Salarial")
        self.generate_salary_certificate_button.setStyleSheet(BUTTON_STYLE)
        self.generate_salary_certificate_button.setFixedWidth(400)
        self.generate_salary_certificate_button.clicked.connect(self.handle_generate_salary_certificate)

        # Add buttons to the layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.generate_fcl_button)
        button_layout.addWidget(self.generate_salary_certificate_button)
        main_layout.addLayout(button_layout)

    def load_requests(self):
        self.unified_requests = UnifiedDocumentRequest.get_all_document_requests()
        self.populate_table(self.unified_requests)

    def populate_table(self, requests: List[Dict[str, str]]) -> None:
        # Sort requests so "Documento no generado" appears first
        sorted_requests = sorted(requests, key=lambda r: r["document_generated"] == "Documento generado")

        self.table.setRowCount(0)
        for req in sorted_requests:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QLabelItem(str(req["employee_name"])))
            self.table.setItem(row, 1, QLabelItem(str(req["employee_national_id"])))
            self.table.setItem(row, 2, QLabelItem(str(req["type"])))
            self.table.setItem(row, 3, QLabelItem(str(req["request_date"])))
            self.table.setItem(row, 4, QLabelItem(str(req["document_generated"])))

    def apply_filters(self):
        filtered = self.unified_requests
        emp_filter = self.employee_filter.text().strip()
        type_filter = self.type_filter.currentText()
        doc_generated_filter = self.document_generated_filter.currentText()
        start_date_filter = self.start_date_filter.date().toPython()
        end_date_filter = self.end_date_filter.date().toPython()

        if emp_filter:
            filtered = [r for r in filtered if emp_filter in r["employee_name"] or emp_filter in r["employee_national_id"]]
        if doc_generated_filter != "Todos":
            filtered = [r for r in filtered if r["document_generated"] == doc_generated_filter]
        if type_filter != "Todos":
            filtered = [r for r in filtered if r["type"] == type_filter]
        if start_date_filter != date(2000, 1, 1):
            filtered = [r for r in filtered if r["request_date"] >= str(start_date_filter)]
        if end_date_filter != date(2100, 12, 31):
            filtered = [r for r in filtered if r["request_date"] <= str(end_date_filter)]

        self.populate_table(filtered)
        
        self.filter_frame.hide()
        self.filter_button.setText(" Filtrar tabla")
        self.repaint()

    def reset_filters(self):
        self.employee_filter.clear()
        self.document_generated_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.start_date_filter.setDate(QDate(2000, 1, 1))
        self.end_date_filter.setDate(QDate(2100, 12, 31))
        self.populate_table(self.unified_requests)
        
        self.filter_frame.hide()
        self.filter_button.setText(" Filtrar tabla")
        self.repaint()

    def update_info_from_selection(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            self.name_label.setText("-")
            self.national_id_label.setText("-")
            self.type_label.setText("-")
            self.requested_on_label.setText("-")
            self.document_generated_label.setText("-")
            self.generate_salary_certificate_button.setEnabled(False)
            self.generate_fcl_button.setEnabled(False)
            return

        selected_request = self.unified_requests[selected_row]
        self.name_label.setText(str(selected_request["employee_name"]))
        self.national_id_label.setText(str(selected_request["employee_national_id"]))
        self.type_label.setText(str(selected_request["type"]))
        self.requested_on_label.setText(str(selected_request["request_date"]))
        self.document_generated_label.setText(str(selected_request["document_generated"]))

        if selected_request["type"] == "Constancia Salarial":
            self.generate_salary_certificate_button.setEnabled(True)
            self.generate_fcl_button.setEnabled(False)
        elif selected_request["type"] == "FCL":
            self.generate_salary_certificate_button.setEnabled(False)
            self.generate_fcl_button.setEnabled(True)
        else:
            self.generate_salary_certificate_button.setEnabled(False)
            self.generate_fcl_button.setEnabled(False)

    def toggle_filter_panel(self):
        self.filter_frame.setVisible(not self.filter_frame.isVisible())
        if self.filter_frame.isVisible():
            self.filter_button.setText(" Ocultar filtros")
        else:
            self.filter_button.setText(" Filtrar tabla")

    def handle_generate_salary_certificate(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una solicitud para generar el documento.")
            return

        selected_request = self.unified_requests[selected_row]

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Constancia Salarial",
            f"{selected_request['employee_name']}_Constancia_Salarial.docx",
            "Documentos de Word (*.docx)"
        )

        if not save_path:
            QMessageBox.warning(self, "Cancelado", "No se seleccionó un archivo para guardar.")
            return

        template_path = "templates/salary_certificate_template.docx"
        
        employee = Employee.get_employee_by_national_id(selected_request["employee_national_id"])

        # Generate the document
        success = generate_salary_certificate(save_path, template_path, {
            "nombre": selected_request["employee_name"],
            "numeroCedula": selected_request["employee_national_id"],
            "departamento": employee.department if employee else "Desconocido",
            "fechaIngreso": selected_request["request_date"],
            "puesto": employee.position if employee else "Desconocido"
        })

        if success:
            QMessageBox.information(self, "Éxito", f"El documento se generó correctamente en:\n{save_path}")
            SalaryCertificate.update_certificate_by_id(
                selected_request["certificate_id"]
            )
            self.populate_table(self.unified_requests)
        else:
            QMessageBox.critical(self, "Error", "No se pudo generar el documento.")

    def handle_generate_fcl(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una solicitud para generar el documento.")
            return

        selected_request = self.unified_requests[selected_row]

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar FCL",
            f"{selected_request['employee_name']}_FCL.docx",
            "Documentos de Word (*.docx)"
        )

        if not save_path:
            QMessageBox.warning(self, "Cancelado", "No se seleccionó un archivo para guardar.")
            return

        template_path = "templates/fcl_template.docx"
        
        employee = Employee.get_employee_by_national_id(selected_request["employee_national_id"])

        # Generate the document
        success = generate_fcl(save_path, template_path, {
            "nombre": selected_request["employee_name"],
            "numeroCedula": selected_request["employee_national_id"],
            "departamento": employee.department if employee else "Desconocido",
            "fechaIngreso": selected_request["request_date"],
            "puesto": employee.position if employee else "Desconocido"
        })

        if success:
            QMessageBox.information(self, "Éxito", f"El documento FCL se generó correctamente en:\n{save_path}")
            FCL.update_fcl_by_id(
                selected_request["certificate_id"]
            )
            self.populate_table(self.unified_requests)
        else:
            QMessageBox.critical(self, "Error", "No se pudo generar el documento FCL.")

# Helper for QTableWidgetItem with alignment
def QLabelItem(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item