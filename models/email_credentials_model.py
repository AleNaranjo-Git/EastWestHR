from db.connection import DatabaseConnection
from typing import Optional, Dict
import logging

class EmailCredentials:
    @staticmethod
    def get_credentials() -> Optional[Dict[str, str]]:
        db = DatabaseConnection()
        conn = db.get_connection("email")

        if not conn:
            logging.error("No se pudo establecer conexión con la base de datos para obtener las credenciales de correo.")
            return None

        cursor = None

        try:
            cursor = conn.cursor()
            sql = "SELECT usuario, clave FROM dbo.VistaInfoCorreo"
            cursor.execute(sql)
            result = cursor.fetchone()

            if result:
                usuario, clave = result
                return {"usuario": usuario, "clave": clave}
            else:
                logging.warning("La vista dbo.VistaInfoCorreo no devolvió resultados.")
                return None
        except Exception as e:
            logging.error(f"Error al obtener las credenciales de correo: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            db.close_connection("email")