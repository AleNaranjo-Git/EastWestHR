from docxtpl import DocxTemplate
import os
import logging

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