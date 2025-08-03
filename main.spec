# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Configuración de rutas
project_root = Path(os.getcwd())
resources_path = project_root / "resources"
templates_path = project_root / "templates"

# Datos a incluir en el ejecutable
datas = [
    (str(resources_path), 'resources'),
    (str(templates_path), 'templates'),
]

# Incluir .env si existe
if os.path.exists('.env'):
    datas.append(('.env', '.'))
else:
    raise FileNotFoundError("Error: .env file is required for building the executable")

# Imports específicos para tus dependencias
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtWidgets', 
    'PySide6.QtGui',
    'PySide6.QtPrintSupport',
    'dotenv',
    'pyodbc',
    'bcrypt',
    'docxtpl',
    'xlsxwriter',
    'holidays',
    'db.connection',
    'logic.auth',
    'logic.date_logic',
    'logic.document_generation',
    'logic.email_service',
    'logic.employee_logic',
    'logic.permits_logic',
    'logic.unified_document_request',
    'logic.unified_requests',
    'logic.user_management',
    'logic.vacations_logic',
    'models.birthday_policy_model',
    'models.employee_model',
    'models.experience_years_policy_model',
    'models.fcl_model',
    'models.permit_request_model',
    'models.permit_type_model',
    'models.role_model',
    'models.salary_certificate_model',
    'models.target_group_model',
    'models.vacation_request_model',
    'ui.components.menu_sidebar',
    'ui.pages.document_request_page',
    'ui.pages.fcl_page',
    'ui.pages.pending_request_page',
    'ui.pages.permits_page',
    'ui.pages.report_generation_page',
    'ui.pages.salary_certificate_page',
    'ui.pages.user_management_page',
    'ui.pages.vacations_page',
    'ui.windows.login_window',
    'ui.windows.main_window',
    'utils.date_utils',
    'utils.dialog_utils',
    'utils.logging_config',
    'utils.resource_path',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'selenium',
        'facebook_scraper',
        'PyQt5',
        'openpyxl',
        'schedule',
        'thefuzz',
        'tkinter',
        'numpy',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EastWestApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(resources_path / 'icons' / 'EW_vertical_logo_800x561.ico') if (resources_path / 'icons' / 'EW_vertical_logo_800x561.ico').exists() else None,
)