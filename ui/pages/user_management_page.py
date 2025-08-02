from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QHeaderView, QFormLayout, QLineEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from resources.styles.components import BUTTON_STYLE, TITLE_STYLE, INPUT_STYLE, CARD_STYLE, MESSAGE_BOX_STYLE
from logic.user_management import get_all_users, create_user, reset_password
from db.connection import DatabaseConnection
from utils.dialog_utils import show_information_dialog, show_warning_dialog, show_critical_dialog


class UserManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_roles()
        self.load_users()

    def setup_ui(self):
        self.setMinimumSize(700, 500)
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Title Section
        title = QLabel("Gestión de Usuarios")
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Form Section
        self.setup_form_section(main_layout)

        # Action Buttons Section
        self.setup_action_buttons(main_layout)

        # Table Section
        self.setup_users_table(main_layout)

    def setup_form_section(self, parent_layout: QVBoxLayout) -> None:
        form_container = QFrame()
        form_container.setFrameShape(QFrame.Shape.StyledPanel)
        form_container.setStyleSheet(CARD_STYLE)
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(12)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setStyleSheet(INPUT_STYLE)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(INPUT_STYLE)

        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText("Identificación")
        self.national_id_input.setStyleSheet(INPUT_STYLE)

        self.role_combo = QComboBox()
        self.role_combo.setStyleSheet(INPUT_STYLE)

        form_layout.addRow("Correo:", self.email_input)
        form_layout.addRow("Contraseña:", self.password_input)
        form_layout.addRow("Identificación:", self.national_id_input)
        form_layout.addRow("Rol:", self.role_combo)

        parent_layout.addWidget(form_container)

    def setup_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        button_container = QFrame()
        button_container.setFrameShape(QFrame.Shape.StyledPanel)
        button_container.setStyleSheet(CARD_STYLE)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(16, 16, 16, 16)
        button_layout.setSpacing(12)

        create_btn = QPushButton("Crear Usuario")
        create_btn.setStyleSheet(BUTTON_STYLE)
        create_btn.clicked.connect(self.create_user)

        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setStyleSheet(BUTTON_STYLE)
        refresh_btn.clicked.connect(self.load_users)

        reset_pwd_btn = QPushButton("Restablecer Contraseña")
        reset_pwd_btn.setStyleSheet(BUTTON_STYLE)
        reset_pwd_btn.clicked.connect(self.reset_password)

        button_layout.addWidget(create_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(reset_pwd_btn)

        parent_layout.addWidget(button_container)

    def setup_users_table(self, parent_layout: QVBoxLayout) -> None:
        table_container = QFrame()
        table_container.setFrameShape(QFrame.Shape.StyledPanel)
        table_container.setStyleSheet(CARD_STYLE)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Correo", "Cédula", "Rol"])
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(250)

        self.table.setStyleSheet("")
        self.table.itemSelectionChanged.connect(self.fill_form_from_selection)

        table_layout.addWidget(self.table)
        parent_layout.addWidget(table_container)

    def load_roles(self) -> None:
        self.role_combo.clear()
        db = DatabaseConnection()
        conn = db.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT nombreRol FROM Rol")
                roles = [row[0] for row in cursor.fetchall()]
                self.role_combo.addItems(roles)
            except Exception as e:
                show_critical_dialog(self, "Error", f"Error loading roles: {e}")
            finally:
                conn.close()

    def load_users(self) -> None:
        """Load users into the table and center the content."""
        users = get_all_users()  # Fetch users directly
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            email_item = QTableWidgetItem(user.correo_login or "")
            email_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            national_id_item = QTableWidgetItem(user.cedula_empleado or "")
            national_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            role_item = QTableWidgetItem(user.id_rol or "")
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row, 0, email_item)
            self.table.setItem(row, 1, national_id_item)
            self.table.setItem(row, 2, role_item)

    def fill_form_from_selection(self) -> None:
        current_row = self.table.currentRow()
        if current_row >= 0:
            email_item = self.table.item(current_row, 0)
            national_id_item = self.table.item(current_row, 1)
            role_item = self.table.item(current_row, 2)

            self.email_input.setText(email_item.text() if email_item else "")
            self.national_id_input.setText(national_id_item.text() if national_id_item else "")
            self.role_combo.setCurrentText(role_item.text() if role_item else "")
            self.password_input.clear()

    def clear_form_fields(self) -> None:
        self.email_input.clear()
        self.password_input.clear()
        self.national_id_input.clear()
        self.role_combo.setCurrentIndex(-1)

    def create_user(self) -> None:
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        national_id = self.national_id_input.text().strip()
        role_name = self.role_combo.currentText()

        if not email or not password:
            show_warning_dialog(self, "Error", "Correo y contraseña son obligatorios.")
            return

        success, message = create_user(email, password, national_id, role_name)
        show_information_dialog(self, "Resultado", message)
        if success:
            self.load_users()
        self.clear_form_fields()

    def reset_password(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            show_warning_dialog(self, "Error", "Seleccione un usuario.")
            return

        email_item = self.table.item(current_row, 0)
        email = email_item.text() if email_item else ""
        new_password = self.password_input.text().strip()

        if not new_password:
            show_warning_dialog(self, "Error", "Por favor ingrese una nueva contraseña en el campo Contraseña.")
            return

        # Confirmation dialog
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Confirmación")
        confirmation.setText(f"¿Está seguro de que desea restablecer la contraseña para {email}?")
        confirmation.setStyleSheet(MESSAGE_BOX_STYLE)

        yes_button = confirmation.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        confirmation.addButton("No", QMessageBox.ButtonRole.NoRole)
        confirmation.setDefaultButton(yes_button)

        confirmation.exec()
        if confirmation.clickedButton() == yes_button:
            success, message = reset_password(email, new_password)
            show_information_dialog(self, "Resultado", message)
            if success:
                self.clear_form_fields()