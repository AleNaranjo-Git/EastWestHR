from docxtpl import DocxTemplate
import os
import logging
import xlsxwriter
from xlsxwriter.worksheet import Worksheet

def generate_salary_certificate(output_path: str, template_path: str, data: dict[str, str]) -> bool:
    try:
        # Load the template
        if not os.path.exists(template_path):
            logging.error(f"Template file not found: {template_path}")
            return False

        doc = DocxTemplate(template_path)

        # Render the template with the provided data
        doc.render(data)

        # Save the generated document
        doc.save(output_path)
        logging.info(f"Salary certificate generated successfully: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error generating salary certificate: {e}")
        return False
    
def generate_fcl(output_path: str, template_path: str, data: dict[str, str]) -> bool:
    try:
        # Load the template
        if not os.path.exists(template_path):
            logging.error(f"Template file not found: {template_path}")
            return False

        doc = DocxTemplate(template_path)

        # Render the template with the provided data
        doc.render(data)

        # Save the generated document
        doc.save(output_path)
        logging.info(f"FCL document generated successfully: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error generating FCL document: {e}")
        return False

def generate_excel_report(output_path: str, data: list[dict[str, str]]) -> bool:
    try:
        # Create an Excel workbook and worksheet
        workbook = xlsxwriter.Workbook(output_path)
        worksheet: Worksheet = workbook.add_worksheet("Report") #type: ignore

        # Define headers
        headers = [
            "Tipo", "Tipo de Permiso", "Nombre del Empleado", "Cédula del Empleado",
            "Fecha de Solicitud", "Fecha de Inicio", "Fecha de Fin", "Hora de Entrada",
            "Hora de Salida", "Cantidad de Días", "Estado", "Nombre del Supervisor"
        ]

        # Write headers to the worksheet
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        # Write data to the worksheet
        for row, record in enumerate(data, start=1):
            worksheet.write(row, 0, record.get("type_", "-"))
            worksheet.write(row, 1, record.get("permit_type_name", "-"))
            worksheet.write(row, 2, record.get("employee_name", "-"))
            worksheet.write(row, 3, record.get("employee_national_id", "-"))
            worksheet.write(row, 4, record.get("request_date", "-"))
            worksheet.write(row, 5, record.get("start_date", "-"))
            worksheet.write(row, 6, record.get("end_date", "-"))
            worksheet.write(row, 7, record.get("check_in_time", "-"))
            worksheet.write(row, 8, record.get("check_out_time", "-"))
            worksheet.write(row, 9, record.get("total_days", "-"))
            worksheet.write(row, 10, record.get("status", "-"))
            worksheet.write(row, 11, record.get("supervisor_name", "-"))

        # Close the workbook
        workbook.close()
        logging.info(f"Excel report generated successfully: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error generating Excel report: {e}")
        return False