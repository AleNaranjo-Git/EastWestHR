from db.connection import DatabaseConnection
import logging
from typing import List, Type, TypeVar

permit_type_t = TypeVar("permit_type_t", bound="PermitType")

class PermitType:
    def __init__(self, permit_type_id: int, permit_type_name: str, is_active: bool):
        self.permit_type_id = permit_type_id
        self.permit_type_name = permit_type_name
        self.is_active = is_active

    @classmethod
    def get_permit_type_by_id(cls, permit_type_id: int):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM TipoPermiso WHERE idTipoPermiso = ?", permit_type_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                
                return cls(
                    permit_type_id=row[0],
                    permit_type_name=row[1],
                    is_active=bool(row[2])
                )
            logging.warning(f"No permit type found with permit_type_id: {permit_type_id}")
            return None
        except Exception as e:
            logging.error(f"Error searching for permit type by id: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_all_active_permits(cls: Type[permit_type_t]) -> List[permit_type_t]:
        db = DatabaseConnection()
        conn = db.connect()
        permit_types: List[permit_type_t] = []
        if conn is None:
            logging.error("No database connection available.")
            return permit_types
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM TipoPermiso WHERE activo = 1")
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                permit_types.append(cls(
                    permit_type_id=row[0],
                    permit_type_name=row[1],
                    is_active=bool(row[2])
                ))
            logging.info(f"Retrieved {len(permit_types)} active permit types.")
            return permit_types
        except Exception as e:
            logging.error(f"Error retrieving active permit types: {e}")
            return []
        finally:
            conn.close()