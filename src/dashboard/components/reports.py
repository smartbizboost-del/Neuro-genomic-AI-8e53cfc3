"""
Report generation components
"""

from typing import Dict, Any
from src.utils.report_generator import generate_clinical_report

def generate_report(data: Dict[str, Any], output_format: str = 'pdf'):
    """Generate a clinical report."""
    return generate_clinical_report(data, output_format=output_format)
