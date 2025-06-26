from models.salary_certificate_model import SalaryCertificate
from models.fcl_model import FCL
from models.employee_model import Employee
from typing import List, Dict, Any
import logging

class UnifiedDocumentRequest:
    @staticmethod
    def get_all_document_requests() -> List[Dict[str, str]]:
        try:
            unified_requests: List[Dict[str, Any]] = []

            # Helper function to translate document_generated
            def translate_document_generated(value: bool) -> str:
                return "Documento generado" if value else "Documento no generado"

            # Get all salary certificate requests
            salary_requests = SalaryCertificate.get_all_certificates()
            for req in salary_requests:
                employee = Employee.get_employee_by_national_id(req.employee_national_id)
                employee_name = (
                    f"{employee.first_name.strip()} {employee.last_name_1.strip()} {employee.last_name_2.strip()}"
                    if employee else req.employee_national_id
                )
                unified_requests.append({
                    "type": "Constancia Salarial",
                    "employee_name": employee_name,
                    "employee_national_id": req.employee_national_id.strip(),
                    "request_date": req.request_date,
                    "document_generated": translate_document_generated(req.document_generated),
                    "certificate_id": req.certificate_id,
                })

            # Get all FCL requests
            fcl_requests = FCL.get_all_fcl()
            for req in fcl_requests:
                employee = Employee.get_employee_by_national_id(req.employee_national_id)
                employee_name = (
                    f"{employee.first_name.strip()} {employee.last_name_1.strip()} {employee.last_name_2.strip()}"
                    if employee else req.employee_national_id
                )
                unified_requests.append({
                    "type": "FCL",
                    "employee_name": employee_name,
                    "employee_national_id": req.employee_national_id.strip(),
                    "request_date": req.request_date,
                    "document_generated": translate_document_generated(req.document_generated),
                    "fcl_id": req.fcl_id,
                })

            logging.info(f"Retrieved {len(unified_requests)} unified document requests.")
            return unified_requests
        except Exception as e:
            logging.error(f"Error retrieving unified document requests: {e}")
            return []