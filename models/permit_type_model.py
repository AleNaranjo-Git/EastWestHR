from db.connection import DatabaseConnection
import uuid
import logging

class PermitType:
    def __init__(self, permit_type_id: uuid.UUID, permit_type_name: str, is_active: bool):
        self.permit_type_id = permit_type_id
        self.permit_type_name = permit_type_name
        self.is_active = is_active

    @classmethod
    def get_permit_type_by_id(cls, permit_type_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM permit_type WHERE permit_type_id = ?", permit_type_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                logging.debug(f"PermitType found with permit_type_id: {permit_type_id[:8]}...")
                return cls(
                    permit_type_id=row[0],
                    permit_type_name=row[1],
                    is_active=bool(row[2])
                )
            logging.warning(f"No permit type found with permit_type_id: {permit_type_id[:8]}...")
            return None
        except Exception as e:
            logging.error(f"Error searching for permit type by id: {e}")
            return None
        finally:
            conn.close()