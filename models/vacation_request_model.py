import logging
from typing import Optional, List
import uuid
from utils.date_utils import parse_date
from datetime import date
from db.connection import DatabaseConnection

class VacationRequest:
    def __init__(
        self,
        request_date: date,
        start_date: date,
        end_date: date,
        total_days: int,
        status: str,
        week_number: int,
        employee_id: uuid.UUID,
        vacation_id: Optional[uuid.UUID] = None,
        approved_by_id: Optional[uuid.UUID] = None
    ):
        self.vacation_id = vacation_id
        self.request_date = request_date
        self.start_date = start_date
        self.end_date = end_date
        self.total_days = total_days
        self.status = status
        self.week_number = week_number
        self.employee_id = employee_id
        self.approved_by_id = approved_by_id

    def save_vacation(self) -> bool:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vacation_request (
                    request_date, start_date, end_date, total_days,
                    status, week_number, employee_id, approved_by_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.request_date,
                self.start_date,
                self.end_date,
                self.total_days,
                self.status,
                self.week_number,
                str(self.employee_id),
                str(self.approved_by_id) if self.approved_by_id else None
            ))
            conn.commit()
            logging.info(f"Vacation saved successfully for employee {self.employee_id}.")
            return True
        except Exception as e:
            logging.error(f"Error saving vacation: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_vacation_by_id(vacation_id: uuid.UUID) -> Optional['VacationRequest']:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vacation_request WHERE vacation_id = ?", (str(vacation_id),))
            row = cursor.fetchone()
            if row:
                logging.debug(f"Vacation found with vacation_id: {vacation_id}")
                return VacationRequest(
                    vacation_id=uuid.UUID(row[0]),
                    request_date=row[1],
                    start_date=row[2],
                    end_date=row[3],
                    total_days=row[4],
                    status=row[5],
                    week_number=row[6],
                    employee_id=uuid.UUID(row[7]),
                    approved_by_id=uuid.UUID(row[8]) if row[8] else None
                )
            logging.warning(f"No vacation found with vacation_id: {vacation_id}")
            return None
        except Exception as e:
            logging.error(f"Error getting vacation: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_vacations_by_employee_id(employee_id: str) -> List['VacationRequest']:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vacation_request WHERE employee_id = ?", (str(employee_id),))
            rows = cursor.fetchall()
            logging.debug(f"Found {len(rows)} vacations for employee {employee_id}.")
            return [
                VacationRequest(
                    vacation_id=uuid.UUID(row[0]),
                    request_date=parse_date(row[1]),
                    start_date=parse_date(row[2]),
                    end_date=parse_date(row[3]),
                    total_days=row[4],
                    status=row[5],
                    week_number=row[6],
                    employee_id=uuid.UUID(row[7]),
                    approved_by_id=uuid.UUID(row[8]) if row[8] else None
                )
                for row in rows
            ]
        except Exception as e:
            logging.error(f"Error getting vacations by employee: {e}")
            return []
        finally:
            conn.close()

    def update_vacation(self) -> bool:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE vacation_request
                SET request_date = ?, start_date = ?, end_date = ?, total_days = ?,
                    status = ?, week_number = ?, employee_id = ?, approved_by_id = ?
                WHERE vacation_id = ?
            """, (
                self.request_date,
                self.start_date,
                self.end_date,
                self.total_days,
                self.status,
                self.week_number,
                str(self.employee_id),
                str(self.approved_by_id) if self.approved_by_id else None,
                str(self.vacation_id)
            ))
            conn.commit()
            logging.info(f"Vacation updated successfully for vacation_id {self.vacation_id}.")
            return True
        except Exception as e:
            logging.error(f"Error updating vacation: {e}")
            return False
        finally:
            conn.close()

    def delete_vacation(self) -> bool:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vacation_request WHERE vacation_id = ?", (str(self.vacation_id),))
            conn.commit()
            logging.info(f"Vacation deleted successfully for vacation_id {self.vacation_id}.")
            return True
        except Exception as e:
            logging.error(f"Error deleting vacation: {e}")
            return False
        finally:
            conn.close()