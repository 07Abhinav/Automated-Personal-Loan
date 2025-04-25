import os

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DOCS_DIR = os.path.join(DATA_DIR, 'raw_documents')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

# OCR Configuration
TESSERACT_CONFIG = r'--oem 3 --psm 6'

# Field patterns for extraction (regex patterns)
FIELD_PATTERNS = {
    'loan_id': r'Loan ID[:]?\s*([A-Z0-9]+)',
    'name': r'(?:Applicant|Name)[:]?\s*([A-Za-z\s]+)',
    'income': r'(?:Annual Income|Income)[:]?\s*(\$?\d+,?\d+)',
    'loan_amount': r'(?:Loan Amount|Amount)[:]?\s*(\$?\d+,?\d+)',
    'address': r'(?:Address|Residence)[:]?\s*([\w\s,\-]+)',
    # Add more patterns as needed
}

# Validation rules
VALIDATION_RULES = {
    'loan_id': {'min_length': 5, 'max_length': 20, 'pattern': r'^[A-Z0-9]+$'},
    'income_annum': {'min_value': 10000, 'max_value': 1000000},
    'loan_amount': {'min_value': 1000, 'max_value': 500000},
    'cibil_score': {'min_value': 300, 'max_value': 900},
}