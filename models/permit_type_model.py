from db.connection import DatabaseConnection
import uuid

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
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM permit_type WHERE permit_type_id = ?", permit_type_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                return cls(
                    permit_type_id=row[0],
                    permit_type_name=row[1],
                    is_active=bool(row[2])
                )
            return None
        except Exception as e:
            print(f"Error searching for permit type by id: {e}")
            return None
        finally:
            conn.close()