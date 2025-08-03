# East West App

East West App es una aplicación para gestionar solicitudes, documentos y permisos de forma eficiente.

---

## Requisitos

- Windows 10 o superior
- Python 3.12+
- Dependencias en `requirements.txt`

---

## Instalación

1. Clona el repositorio:
   ```bash
   git clone git@github.com:AleNaranjo-Git/EastWestHR.git
   cd EastWestHR
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## Ejecutar en modo desarrollo

```bash
python main.py
```

---

## Generar ejecutable (.exe)

1. Instala PyInstaller (solo una vez):
   ```bash
   pip install pyinstaller
   ```

2. Genera el ejecutable en consola:
   ```bash
   build.bat
   ```
   El ejecutable se guardará en la carpeta `dist/`.

---

## Estructura del proyecto

- `db/` - Conexión a la Base de Datos
- `logic/` – Lógica de negocio
- `models/` – Modelos de datos
- `resources/` - Iconos y estilos
- `templates/` - Templates para generar documentos
- `ui/` – Interfaz gráfica
- `utils/` – Funciones auxiliares
- `main.py` – Punto de entrada
- `requirements.txt` – Dependencias

---

## Notas importantes

- Debes tener un archivo `.env` en la raíz del proyecto con la configuración necesaria (por ejemplo, credenciales de base de datos).

---