from db.connection import DatabaseConnection
import uuid

class Position:
    def __init__(self, position_id: uuid.UUID, position_name: str):
        self.position_id = position_id
        self.position_name = position_name

    @classmethod
    def get_position_by_id(cls, position_id: str):
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM position WHERE position_id = ?", position_id)
            row = cursor.fetchone()
            cursor.close()
            if row:
                return cls(
                    position_id=row[0],
                    position_name=row[1]
                )
            return None
        except Exception as e:
            print(f"Error searching for position by id: {e}")
            return None
        finally:
            conn.close()