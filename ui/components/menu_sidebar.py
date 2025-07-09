from typing import Dict, cast
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication, QMessageBox
from PySide6.QtCore import Qt, QPoint, QObject, QEvent
from PySide6.QtGui import QColor, QPalette, QMouseEvent
from resources.styles.colors import SIDEBAR_BG
from resources.styles.components import SIDEBAR_BUTTON_STYLE, MESSAGE_BOX_STYLE
from logic.auth import Session, logout
from ui.windows.login_window import LoginWindow

class MenuSidebar(QWidget):
    def __init__(self, parent_window: QWidget):
        super().__init__()
        self.parent_window: QWidget = parent_window
        self.buttons: Dict[str, QPushButton] = {}
        self.login_window: LoginWindow | None = None

        # Sidebar setup
        self.setFixedWidth(220)
        self.setObjectName("Sidebar")
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(SIDEBAR_BG))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setStyleSheet(SIDEBAR_BUTTON_STYLE)

        # Layout setup
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 30, 10, 20)
        layout.setSpacing(10)

        # Sidebar buttons
        names = [
            ("Vacaciones", "Solicitar Vacación"),
            ("Permisos", "Solicitar Permiso"),
            ("Constancia", "Constancia Salarial"),
            ("FCL", "FCL"),
            ("Pendiente Aprobar", "Pendiente Aprobar"),
            ("Generar Documento", "Generar Documento"),
            ("Generar Reporte", "Generar Reporte"),
        ]

        for key, label in names:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setMinimumHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Login/logout button
        self.login_logout_button = QPushButton("Iniciar Sesión")
        self.login_logout_button.setMinimumHeight(44)
        self.login_logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_logout_button.clicked.connect(self._handle_login_logout)
        layout.addWidget(self.login_logout_button)

        self.setLayout(layout)

        self.buttons["Vacaciones"].setChecked(True)

        for btn in self.buttons.values():
            btn.clicked.connect(self._handle_button_checked)

        self.update_login_logout_button()

    def _handle_button_checked(self):
        clicked_button = cast(QPushButton, self.sender())
        for btn in self.buttons.values():
            if btn != clicked_button:
                btn.setChecked(False)
        clicked_button.setChecked(True)

    def _handle_login_logout(self):
        if Session.current_user is None:
            self._show_login_confirmation()
        else:
            self._show_logout_confirmation()

    def _open_login_window(self):
        try:
            self.parent_window.close()
            self.login_window = LoginWindow()
            self.login_window.show()
        except Exception as e:
            print(f"Error opening LoginWindow: {e}")

    def _logout_and_reopen_main_window(self):
        logout()
        self.parent_window.close()
        new_main_window = self.parent_window.__class__()
        new_main_window.show()

    def update_login_logout_button(self):
        if Session.current_user is None:
            self.login_logout_button.setText("Iniciar Sesión")
        else:
            self.login_logout_button.setText(Session.current_user.get("correoLogin", "Cerrar Sesión"))

    def _install_event_filter(self, panel: QWidget):
        class PanelEventFilter(QObject):
            def __init__(self, parent_widget: QWidget, panel: QWidget):
                super().__init__(parent_widget)
                self.parent_widget: QWidget = parent_widget
                self.panel: QWidget = panel

            def eventFilter(self, obj: QObject, event: QEvent) -> bool:
                if isinstance(event, QMouseEvent) and event.type() == QEvent.Type.MouseButtonPress:
                    global_pos = event.globalPos()
                    if not self.panel.geometry().contains(global_pos - self.parent_widget.mapToGlobal(QPoint(0, 0))):
                        self.panel.close()
                        self.parent_widget.removeEventFilter(self)
                return super().eventFilter(obj, event)

        filter = PanelEventFilter(self, panel)
        app_instance = QApplication.instance()
        if app_instance:
            app_instance.installEventFilter(filter)

    def _show_login_confirmation(self):
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Confirmación")
        confirmation.setText("<b>¿Desea iniciar sesión?</b>")
        confirmation.setIcon(QMessageBox.Icon.Question)
        confirmation.setStyleSheet(MESSAGE_BOX_STYLE)
        confirmation.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirmation.setDefaultButton(QMessageBox.StandardButton.Yes)

        result = confirmation.exec()
        if result == QMessageBox.StandardButton.Yes:
            self._open_login_window()

    def _show_logout_confirmation(self):
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Confirmación")
        confirmation.setText("<b>¿Desea cerrar sesión?</b>")
        confirmation.setIcon(QMessageBox.Icon.Warning)
        confirmation.setStyleSheet(MESSAGE_BOX_STYLE)
        confirmation.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirmation.setDefaultButton(QMessageBox.StandardButton.Yes)

        result = confirmation.exec()
        if result == QMessageBox.StandardButton.Yes:
            self._logout_and_reopen_main_window()
