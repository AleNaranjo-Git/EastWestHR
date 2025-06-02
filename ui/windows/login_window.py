from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from logic.auth import authenticate, AuthResult
from resources.styles.components import (
    INPUT_STYLE,
    BUTTON_STYLE,
    TITLE_STYLE,
    ERROR_LABEL_STYLE,
    BACKGROUND
)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de sesión")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(f"background-color: {BACKGROUND};")
        self.setup_ui()
        self.showMaximized()

    def setup_ui(self):
        # Main horizontal layout to center logo and form
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Left spacer to help center content
        main_layout.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # --- Company logo, always centered and fixed size ---
        img_label = QLabel()
        pixmap = QPixmap("resources/icons/EW_vertical_logo_1000x702.png")
        img_label.setPixmap(
            pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio,
                          Qt.TransformationMode.SmoothTransformation)
        )
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setFixedWidth(400)
        img_label.setFixedHeight(400)
        main_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Login form container, fixed size and centered ---
        form_container = QWidget()
        form_container.setFixedWidth(400)
        form_container.setFixedHeight(400)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Form title
        title = QLabel("Iniciar sesión")
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title)

        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.username_input)

        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.setFixedHeight(40)
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)

        # Error message label
        self.error_label = QLabel()
        self.error_label.setStyleSheet(ERROR_LABEL_STYLE)
        self.error_label.setWordWrap(True)
        self.error_label.setText("")
        self.error_label.setMinimumHeight(30)
        form_layout.addWidget(self.error_label)

        # Add the form container to the main layout, centered
        main_layout.addWidget(form_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Right spacer to help center content
        main_layout.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

    def login(self) -> None:
        email: str = self.username_input.text().strip()
        password: str = self.password_input.text().strip()

        if not email:
            self.error_label.setText("Por favor ingrese su correo electrónico.")
            return
        if not password:
            self.error_label.setText("Por favor ingrese su contraseña.")
            return

        # Error message dictionary
        error_messages = {
            "connection_error": "Error de conexión con el servidor.",
            "invalid_user": "Usuario no encontrado.",
            "invalid_password": "Contraseña incorrecta."
        }

        try:
            result: AuthResult = authenticate(email, password)
            if result == "success":
                from ui.windows.main_window import MainWindow
                self.main_window = MainWindow()
                self.main_window.show()
                self.close()
            else:
                self.error_label.setText(error_messages.get(result, "Error inesperado."))
        except Exception as e:
            print(f"Login error: {str(e)}")
            self.error_label.setText("Error inesperado en el sistema.")
