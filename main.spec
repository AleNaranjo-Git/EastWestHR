# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Configuración de rutas
project_root = Path(os.getcwd())
resources_path = project_root / "resources"
templates_path = project_root / "templates"

# Datos a incluir en el ejecutable
datas = [
    # Incluir carpeta de recursos (iconos, estilos)
    (str(resources_path), 'resources'),
    # Incluir templates para generación de documentos
    (str(templates_path), 'templates'),
]

# Incluir .env si existe (opcional)
if os.path.exists('.env'):
    datas.append(('.env', '.'))

# Imports específicos para tus dependencias
hiddenimports = [
    # PySide6 módulos
    'PySide6.QtCore',
    'PySide6.QtWidgets', 
    'PySide6.QtGui',
    'PySide6.QtPrintSupport',
    
    # Tus dependencias principales
    'dotenv',
    'pyodbc',
    'bcrypt',
    'docxtpl',
    'xlsxwriter',
    'holidays',
    
    # Módulos de tu aplicación
    'db.connection',
    'logic.document_generation',
    'logic.vacations_logic',
    'logic.permits_logic',
    'models.employee_model',
    'ui.windows.main_window',
    'ui.pages',
    'ui.components',
    'utils.logging_config',
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
        # Excluir librerías pesadas que no necesitas
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
    console=False,  # False = aplicación GUI sin ventana de consola
    disable_windowed_traceback=False,
    target_arch=None,
    coinstaller=False,
    entitlements_file=None,
    icon=str(resources_path / 'icons' / 'EW_vertical_logo_800x561.ico') if (resources_path / 'icons' / 'EW_vertical_logo_800x561.ico').exists() else None,
)