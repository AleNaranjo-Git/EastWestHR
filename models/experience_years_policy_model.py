from typing import Optional, List
from datetime import date
from db.connection import DatabaseConnection
import logging

class ExperienceYearsPolicy:
    def __init__(
        self,
        policy_id: int,
        years_from: int,
        years_to: Optional[int],
        allowed_days: int,
        vacation_condition: str,
        effective_start_date: date,
        effective_end_date: Optional[date],
        is_active: bool,
        target_group_id: int,
        approval_role_id: int
    ):
        self.policy_id = policy_id
        self.years_from = years_from
        self.years_to = years_to
        self.allowed_days = allowed_days
        self.vacation_condition = vacation_condition
        self.effective_start_date = effective_start_date
        self.effective_end_date = effective_end_date
        self.is_active = is_active
        self.target_group_id = target_group_id
        self.approval_role_id = approval_role_id

    @staticmethod
    def create_experience_years_policy(
        years_from: int,
        years_to: Optional[int],
        allowed_days: int,
        vacation_condition: str,
        effective_start_date: date,
        effective_end_date: Optional[date],
        is_active: bool,
        target_group_id: int,
        approval_role_id: int
    ) -> Optional["ExperienceYearsPolicy"]:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO PoliticaAniosExperiencia (
                    aniosDesde,
                    aniosHasta,
                    diasPermitidos,
                    condicionVacaciones,
                    fechaInicioVigencia,
                    fechaFinVigencia,
                    activo,
                    idGrupoObjetivo,
                    idRolAprobacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                years_from,
                years_to,
                allowed_days,
                vacation_condition,
                effective_start_date,
                effective_end_date,
                int(is_active),
                target_group_id,
                approval_role_id
            ))
            cursor.execute("SELECT SCOPE_IDENTITY()")
            policy_id_row = cursor.fetchone()
            policy_id = int(policy_id_row[0]) if policy_id_row and policy_id_row[0] is not None else None
            conn.commit()
            if policy_id is None:
                logging.error("Failed to retrieve the new policy ID after insert.")
                return None
            logging.info(f"Experience years policy {policy_id} created successfully.")
            return ExperienceYearsPolicy(
                policy_id,
                years_from,
                years_to,
                allowed_days,
                vacation_condition,
                effective_start_date,
                effective_end_date,
                is_active,
                target_group_id,
                approval_role_id
            )
        except Exception as e:
            logging.error(f"Error creating experience years policy: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all_active_experience_years_policies() -> List["ExperienceYearsPolicy"]:
        db = DatabaseConnection()
        conn = db.connect()
        policies: List[ExperienceYearsPolicy] = []
        if conn is None:
            logging.error("Could not connect to the database.")
            return policies
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM PoliticaAniosExperiencia
                WHERE activo = 1
            """)
            rows = cursor.fetchall()
            for row in rows:
                policies.append(ExperienceYearsPolicy(
                    policy_id=row[0],
                    years_from=row[1],
                    years_to=row[2],
                    allowed_days=row[3],
                    vacation_condition=row[4],
                    effective_start_date=row[5],
                    effective_end_date=row[6],
                    is_active=bool(row[7]),
                    target_group_id=row[8],
                    approval_role_id=row[9]
                ))
            logging.info(f"Retrieved {len(policies)} active experience years policies.")
            return policies
        except Exception as e:
            logging.error(f"Error retrieving active experience years policies: {e}")
            return []
        finally:
            conn.close()