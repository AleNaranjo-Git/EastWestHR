from typing import Optional, List
from datetime import date
from db.connection import DatabaseConnection
import logging

class BirthdayPolicy:
    def __init__(
        self,
        birthday_policy_id: int,
        available_days_range: int,
        only_birth_month: bool,
        effective_start_date: date,
        effective_end_date: Optional[date],
        is_active: bool,
        target_group_id: int
    ):
        self.birthday_policy_id = birthday_policy_id
        self.available_days_range = available_days_range
        self.only_birth_month = only_birth_month
        self.effective_start_date = effective_start_date
        self.effective_end_date = effective_end_date
        self.is_active = is_active
        self.target_group_id = target_group_id

    @staticmethod
    def create_birthday_policy(
        available_days_range: int,
        only_birth_month: bool,
        effective_start_date: date,
        effective_end_date: Optional[date],
        is_active: bool,
        target_group_id: int
    ) -> Optional["BirthdayPolicy"]:
        db = DatabaseConnection()
        conn = db.get_connection("main")
        if conn is None:
            logging.error("Could not connect to the database.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO PoliticaCumpleanios (
                    rangoDiasDisponibles,
                    soloMesCumpleanios,
                    fechaInicioVigencia,
                    fechaFinVigencia,
                    activo,
                    idGrupoObjetivo
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                available_days_range,
                int(only_birth_month),
                effective_start_date,
                effective_end_date,
                int(is_active),
                target_group_id
            ))
            cursor.execute("SELECT SCOPE_IDENTITY()")
            policy_id_row = cursor.fetchone()
            birthday_policy_id = int(policy_id_row[0]) if policy_id_row and policy_id_row[0] is not None else None
            conn.commit()
            if birthday_policy_id is None:
                logging.error("Failed to retrieve the new birthday policy ID after insert.")
                return None
            logging.info(f"Birthday policy {birthday_policy_id} created successfully.")
            return BirthdayPolicy(
                birthday_policy_id,
                available_days_range,
                only_birth_month,
                effective_start_date,
                effective_end_date,
                is_active,
                target_group_id
            )
        except Exception as e:
            logging.error(f"Error creating birthday policy: {e}")
            return None
        finally:
            db.close_connection("main")

    @staticmethod
    def get_all_active_birthday_policies() -> List["BirthdayPolicy"]:
        db = DatabaseConnection()
        conn = db.get_connection("main")
        policies: List[BirthdayPolicy] = []
        if conn is None:
            logging.error("Could not connect to the database.")
            return policies
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM PoliticaCumpleanios
                WHERE activo = 1
            """)
            rows = cursor.fetchall()
            for row in rows:
                policies.append(BirthdayPolicy(
                    birthday_policy_id=row[0],
                    available_days_range=row[1],
                    only_birth_month=bool(row[2]),
                    effective_start_date=row[3],
                    effective_end_date=row[4],
                    is_active=bool(row[5]),
                    target_group_id=row[6]
                ))
            logging.info(f"Retrieved {len(policies)} active birthday policies.")
            return policies
        except Exception as e:
            logging.error(f"Error retrieving active birthday policies: {e}")
            return []
        finally:
            db.close_connection("main")