# utils/resource_path.py
import sys
import os

def get_resource_path(relative_path: str) -> str:
    """
    Obtiene la ruta correcta para recursos, funciona tanto en desarrollo como en ejecutable.
    """
    try:
        # PyInstaller crea un temp folder y almacena path en _MEIPASS
        base_path: str = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        # Desarrollo - usar directorio del script actual
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)