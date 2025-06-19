from typing import Optional, List
from datetime import date, time
from db.connection import DatabaseConnection
import logging

class PermitRequest:
    def __init__(
        self,
        permit_request_id: int,
        request_date: date,
        absence_date: date,
        check_in_time: time,
        check_out_time: time,
        status: str,
        week_number: int,
        employee_national_id: str,
        permit_type_id: int,
        approver_national_id: Optional[str] = None
    ):
        self.permit_request_id = permit_request_id
        self.request_date = request_date
        self.absence_date = absence_date
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.status = status
        self.week_number = week_number
        self.employee_national_id = employee_national_id
        self.permit_type_id = permit_type_id
        self.approver_national_id = approver_national_id

    @staticmethod
    def get_permit_by_id(permit_request_id: int) -> Optional["PermitRequest"]:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("Could not connect to the database.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM SolicitudPermiso
                WHERE idSolicitudPermiso = ?
            """, (permit_request_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return PermitRequest(
                    permit_request_id=row[0],
                    request_date=row[1],
                    absence_date=row[2],
                    check_in_time=row[3],
                    check_out_time=row[4],
                    status=row[5],
                    week_number=row[6],
                    employee_national_id=row[7],
                    permit_type_id=row[8],
                    approver_national_id=row[9]
                )
            else:
                logging.warning(f"Permit not found for id: {permit_request_id}")
                return None
        except Exception as e:
            logging.error(f"Error retrieving permit: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_permits_by_employee_national_id(employee_national_id: str) -> List["PermitRequest"]:
        db = DatabaseConnection()
        conn = db.connect()
        permits: List[PermitRequest] = []
        if conn is None:
            logging.error("Could not connect to the database.")
            return permits
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM SolicitudPermiso
                WHERE cedulaEmpleado = ?
            """, (employee_national_id,))
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                permits.append(PermitRequest(
                    permit_request_id=row[0],
                    request_date=row[1],
                    absence_date=row[2],
                    check_in_time=row[3],
                    check_out_time=row[4],
                    status=row[5],
                    week_number=row[6],
                    employee_national_id=row[7],
                    permit_type_id=row[8],
                    approver_national_id=row[9]
                ))
            return permits
        except Exception as e:
            logging.error(f"Error retrieving permits by employee_national_id: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def save_permit(
        request_date: date,
        absence_date: date,
        check_in_time: time,
        check_out_time: time,
        status: str,
        week_number: int,
        employee_national_id: str,
        permit_type_id: int,
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
                INSERT INTO SolicitudPermiso (
                    fechaSolicitud, fechaAusencia, horaEntrada, horaSalida,
                    estado, numeroSemana, cedulaEmpleado, idTipoPermiso, cedulaAprobador
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_date,
                absence_date,
                check_in_time,
                check_out_time,
                status,
                week_number,
                employee_national_id,
                permit_type_id,
                approver_national_id
            ))
            conn.commit()
            logging.info("Permit saved successfully.")
            return True
        except Exception as e:
            logging.error(f"Error saving permit: {e}")
            return False
        finally:
            conn.close()