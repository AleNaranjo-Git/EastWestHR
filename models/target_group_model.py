from typing import Optional
from db.connection import DatabaseConnection
import logging

class TargetGroup:
    def __init__(
        self,
        target_group_id: int,
        target_group_name: str
    ):
        self.target_group_id = target_group_id
        self.target_group_name = target_group_name

    @staticmethod
    def get_target_group_by_id(target_group_id: int) -> Optional["TargetGroup"]:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM GrupoObjetivo
                WHERE idGrupoObjetivo = ?
            """, (target_group_id,))
            row = cursor.fetchone()
            if row:
                return TargetGroup(
                    target_group_id=row[0],
                    target_group_name=row[1]
                )
            else:
                logging.warning(f"Target group not found for id: {target_group_id}")
                return None
        except Exception as e:
            logging.error(f"Error retrieving target group: {e}")
            return None
        finally:
            conn.close()