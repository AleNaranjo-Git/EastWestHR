from db.connection import DatabaseConnection
import logging
from typing import Optional, List
from datetime import date

class SalaryCertificate:
    def __init__(self, certificate_id: int, request_date: date, employee_national_id: str, document_generated: bool):
        self.certificate_id = certificate_id
        self.request_date = request_date
        self.employee_national_id = employee_national_id
        self.document_generated = document_generated

    @classmethod
    def get_certificate_by_id(cls, certificate_id: int) -> Optional["SalaryCertificate"]:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT idCertificadoSalario, fechaSolicitud, cedulaEmpleado, documentoGenerado FROM CertificadoSalario WHERE idCertificadoSalario = ?", (certificate_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return cls(
                    certificate_id=row[0],
                    request_date=row[1],
                    employee_national_id=row[2].strip(),
                    document_generated=bool(row[3])
                )
            logging.warning(f"No salary certificate found with id: {certificate_id}")
            return None
        except Exception as e:
            logging.error(f"Error retrieving salary certificate by id: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_all_certificates(cls) -> List["SalaryCertificate"]:
        db = DatabaseConnection()
        conn = db.connect()
        certificates: List["SalaryCertificate"] = []
        if conn is None:
            logging.error("No database connection available.")
            return certificates
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT idCertificadoSalario, fechaSolicitud, cedulaEmpleado, documentoGenerado FROM CertificadoSalario ORDER BY documentoGenerado ASC")
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                certificates.append(cls(
                    certificate_id=row[0],
                    request_date=row[1],
                    employee_national_id=row[2].strip(),
                    document_generated=bool(row[3])
                ))
            logging.info(f"Retrieved {len(certificates)} salary certificates.")
            return certificates
        except Exception as e:
            logging.error(f"Error retrieving all salary certificates: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def create_certificate(cls, request_date: date, employee_national_id: str, document_generated: bool) -> Optional[int]:
        db = DatabaseConnection()
        conn = db.connect()
        if conn is None:
            logging.error("No database connection available.")
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO CertificadoSalario (fechaSolicitud, cedulaEmpleado, documentoGenerado) VALUES (?, ?, ?)",
                (request_date, employee_national_id, document_generated)
            )
            conn.commit()
            logging.info(f"Created new salary certificate request ")
            return True
        except Exception as e:
            logging.error(f"Error creating salary certificate request: {e}")
            return False
        finally:
            conn.close()

    @classmethod
    def update_certificate_by_id(cls, certificate_id: str) -> bool:
        """
        Updates the documentoGenerado field of a specific salary certificate to 1.

        :param certificate_id: The ID of the salary certificate to update.
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
                "UPDATE CertificadoSalario SET documentoGenerado = 1 WHERE idCertificadoSalario = ?",
                (certificate_id,)
            )
            conn.commit()
            logging.info(f"Updated documentoGenerado to 1 for certificate ID: {certificate_id}")
            return True
        except Exception as e:
            logging.error(f"Error updating documentoGenerado for certificate ID {certificate_id}: {e}")
            return False
        finally:
            conn.close()