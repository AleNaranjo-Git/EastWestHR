from db.connection import DatabaseConnection
import logging
from typing import Optional, List
from datetime import date

class FCL:
    def __init__(self, fcl_id: int, request_date: date, employee_national_id: str, document_generated: bool):
        self.fcl_id = fcl_id
        self.request_date = request_date
        self.employee_national_id = employee_national_id
        self.document_generated = document_generated

    @classmethod
    def get_fcl_by_id(cls, fcl_id: int) -> Optional["FCL"]:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT idFCL, fechaSolicitud, cedulaEmpleado, documentoGenerado FROM FCL WHERE idFCL = ?", (fcl_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return cls(
                    fcl_id=row[0],
                    request_date=row[1],
                    employee_national_id=row[2],
                    document_generated=bool(row[3])
                )
            logging.warning(f"No FCL record found with id: {fcl_id}")
            return None
        except Exception as e:
            logging.error(f"Error retrieving FCL record by id: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_all_fcl(cls) -> List["FCL"]:
        db = DatabaseConnection()
        conn = db.connect()
        fcl_records: List["FCL"] = []
        if conn is None:
            logging.error("No database connection available.")
            return fcl_records
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT idFCL, fechaSolicitud, cedulaEmpleado, documentoGenerado FROM FCL ORDER BY documentoGenerado ASC")
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                fcl_records.append(cls(
                    fcl_id=row[0],
                    request_date=row[1],
                    employee_national_id=row[2],
                    document_generated=bool(row[3])
                ))
            logging.info(f"Retrieved {len(fcl_records)} FCL records.")
            return fcl_records
        except Exception as e:
            logging.error(f"Error retrieving all FCL records: {e}")
            return []
        finally:
            conn.close()
            
    @classmethod
    def create_fcl(cls, request_date: date, employee_national_id: str, document_generated: bool) -> Optional[int]:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO FCL (fechaSolicitud, cedulaEmpleado, documentoGenerado) VALUES (?, ?, ?)",
                (request_date, employee_national_id, document_generated)
            )
            conn.commit()
            logging.info(f"Created new FCL request ")
            return True
        except Exception as e:
            logging.error(f"Error creating FCL request: {e}")
            return False
        finally:
            conn.close()
    
    @classmethod
    def update_fcl_by_id(cls, fcl_id: str) -> bool:
        """
        Updates the documentoGenerado field of a specific FCL record to 1.

        :param fcl_id: The ID of the FCL record to update.
        :return: True if the update was successful, False otherwise.
        """
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE FCL SET documentoGenerado = 1 WHERE idFCL = ?",
                (fcl_id,)
            )
            conn.commit()
            logging.info(f"Updated documentoGenerado to 1 for FCL ID: {fcl_id}")
            return True
        except Exception as e:
            logging.error(f"Error updating documentoGenerado for FCL ID {fcl_id}: {e}")
            return False
        finally:
            conn.close()