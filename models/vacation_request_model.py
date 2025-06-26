import logging
from typing import Optional, List
from utils.date_utils import parse_date
from datetime import date
from db.connection import DatabaseConnection

class VacationRequest:
    def __init__(
        self,
        vacation_request_id: int,
        request_date: date,
        start_date: date,
        end_date: date,
        total_days: int,
        status: str,
        week_number: int,
        employee_national_id: str,
        approver_national_id: Optional[str] = None
    ):
        self.vacation_request_id = vacation_request_id
        self.request_date = request_date
        self.start_date = start_date
        self.end_date = end_date
        self.total_days = total_days
        self.status = status
        self.week_number = week_number
        self.employee_national_id = employee_national_id
        self.approver_national_id = approver_national_id

    @staticmethod
    def save_vacation(
        request_date: date,
        start_date: date,
        end_date: date,
        total_days: int,
        status: str,
        week_number: int,
        employee_national_id: str,
        approver_national_id: Optional[str] = None
    ) -> bool:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO SolicitudVacaciones (
                    fechaSolicitud, fechaInicio, fechaFin, totalDias,
                    estado, numeroSemana, cedulaEmpleado, cedulaAprobador
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_date,
                start_date,
                end_date,
                total_days,
                status,
                week_number,
                employee_national_id,
                approver_national_id
            ))
            conn.commit()
            logging.info(f"Vacation saved successfully for employee {employee_national_id}.")
            return True
        except Exception as e:
            logging.error(f"Error saving vacation: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_vacation_by_id(vacation_request_id: int) -> Optional['VacationRequest']:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM SolicitudVacaciones WHERE idSolicitudVacaciones = ?", (vacation_request_id,))
            row = cursor.fetchone()
            if row:
                return VacationRequest(
                    vacation_request_id=row[0],
                    request_date=row[1],
                    start_date=row[2],
                    end_date=row[3],
                    total_days=row[4],
                    status=row[5],
                    week_number=row[6],
                    employee_national_id=row[7],
                    approver_national_id=row[8]
                )
            logging.warning(f"No vacation found with id: {vacation_request_id}")
            return None
        except Exception as e:
            logging.error(f"Error getting vacation: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_vacations_by_employee_national_id(employee_national_id: str) -> List['VacationRequest']:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM SolicitudVacaciones WHERE cedulaEmpleado = ?", (employee_national_id,))
            rows = cursor.fetchall()
            logging.debug(f"Found {len(rows)} vacations for employee {employee_national_id}.")
            return [
                VacationRequest(
                    vacation_request_id=row[0],
                    request_date=parse_date(row[1]),
                    start_date=parse_date(row[2]),
                    end_date=parse_date(row[3]),
                    total_days=row[4],
                    status=row[5],
                    week_number=row[6],
                    employee_national_id=row[7],
                    approver_national_id=row[8]
                )
                for row in rows
            ]
        except Exception as e:
            logging.error(f"Error getting vacations by employee: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def update_vacation(
        vacation_request_id: int,
        request_date: date,
        start_date: date,
        end_date: date,
        total_days: int,
        status: str,
        week_number: int,
        employee_national_id: str,
        approver_national_id: Optional[str] = None
    ) -> bool:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE SolicitudVacaciones
                SET fechaSolicitud = ?, fechaInicio = ?, fechaFin = ?, totalDias = ?,
                    estado = ?, numeroSemana = ?, cedulaEmpleado = ?, cedulaAprobador = ?
                WHERE idSolicitudVacaciones = ?
            """, (
                request_date,
                start_date,
                end_date,
                total_days,
                status,
                week_number,
                employee_national_id,
                approver_national_id,
                vacation_request_id
            ))
            conn.commit()
            logging.info(f"Vacation updated successfully for id {vacation_request_id}.")
            return True
        except Exception as e:
            logging.error(f"Error updating vacation: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete_vacation(vacation_request_id: int) -> bool:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM SolicitudVacaciones WHERE idSolicitudVacaciones = ?", (vacation_request_id,))
            conn.commit()
            logging.info(f"Vacation deleted successfully for id {vacation_request_id}.")
            return True
        except Exception as e:
            logging.error(f"Error deleting vacation: {e}")
            return False
        finally:
            conn.close()
            
    @staticmethod
    def get_vacations_by_supervisor_id(supervisor_national_id: str) -> List["VacationRequest"]:
        db = DatabaseConnection()
        conn = db.connect()
        vacations: List[VacationRequest] = []
        if conn is None:
            logging.error("Could not connect to the database.")
            return vacations
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM SolicitudVacaciones
                WHERE cedulaAprobador = ?
            """, (supervisor_national_id,))
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                vacations.append(VacationRequest(
                    vacation_request_id=row[0],
                    request_date=row[1],
                    start_date=row[2],
                    end_date=row[3],
                    total_days=row[4],
                    status=row[5],
                    week_number=row[6],
                    employee_national_id=row[7],
                    approver_national_id=row[8]
                ))
            return vacations
        except Exception as e:
            logging.error(f"Error retrieving vacations by supervisor_id: {e}")
            return []
        finally:
            conn.close()
            
    @staticmethod
    def update_status(vacation_request_id: int, new_status: str) -> bool:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE SolicitudVacaciones SET estado = ? WHERE idSolicitudVacaciones = ?",
                (new_status, vacation_request_id)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error updating vacation status: {e}")
            return False
        finally:
            conn.close()