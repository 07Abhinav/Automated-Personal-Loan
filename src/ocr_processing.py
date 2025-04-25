import pytesseract
import re
import spacy
import cv2
import numpy as np
from typing import Dict, Union
from pdf2image import convert_from_path

# Initialize spaCy for advanced text processing
nlp = spacy.load("en_core_web_sm")

def extract_text_from_image(image: Union[str, np.ndarray]) -> str:
    """Extract text from image with preprocessing"""
    # Preprocess image
    if isinstance(image, str):
        img = cv2.imread(image)
    else:
        img = image
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Perform OCR
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config=custom_config)
    return text

def extract_loan_fields(text: str) -> Dict[str, str]:
    """Extract structured loan application data with robust regex"""
    # Normalize text: remove extra spaces, unify spacing
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)

    # Improved regex patterns (more flexible and tolerant to OCR errors)
    patterns = {
        'applicant_name': r'Applicant\s*Name\s*[:\-]?\s*(.+)',
        'address': r'Address\s*[:\-]?\s*(.+)',
        'dob': r'Date\s*of\s*Birth\s*[:\-]?\s*(\d{2}[-/]\d{2}[-/]\d{4})',
        'education': r'Education\s*[:\-]?\s*(Graduate|Not Graduate|Undergraduate)',
        'self_employed': r'Self\s*Employed\s*[:\-]?\s*(Yes|No)',
        'no_of_dependents': r'(?:Number\s*of\s*)?Dependents\s*[:\-]?\s*(\d+)',
        'income_annum': r'Annual\s*Income\s*[:\-]?\s*₹?\s*([\d,]+)',
        'loan_amount': r'Loan\s*Amount\s*(?:Requested)?\s*[:\-]?\s*₹?\s*([\d,]+)',
        'loan_term': r'Loan\s*Term\s*[:\-]?\s*(\d+)',
        'cibil_score': r'CIBIL\s*Score\s*[:\-]?\s*(\d+)',
        'residential_assets': r'Residential\s*Assets\s*[:\-]?\s*₹?\s*([\d,]+)',
        'commercial_assets': r'Commercial\s*Assets\s*[:\-]?\s*₹?\s*([\d,]+)',
        'luxury_assets': r'Luxury\s*Assets\s*[:\-]?\s*₹?\s*([\d,]+)',
        'bank_assets': r'Bank\s*Assets\s*[:\-]?\s*₹?\s*([\d,]+)'
    }

    extracted = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted[field] = match.group(1).strip()

    # Clean numeric fields (remove commas)
    for field in ['income_annum', 'loan_amount', 'residential_assets',
                  'commercial_assets', 'luxury_assets', 'bank_assets']:
        if field in extracted:
            extracted[field] = extracted[field].replace(',', '')

    return extracted

    """Extract structured loan application data"""
    # Field patterns with improved regex
    patterns = {
        'applicant_name': r'Applicant Name\s*:\s*(.+?)\s*(?=\n|Address)',
        'address': r'Address\s*:\s*(.+?)\s*(?=\n|Date of Birth)',
        'dob': r'Date of Birth\s*:\s*(\d{2}-\d{2}-\d{4})',
        'education': r'Education\s*:\s*(.+?)\s*(?=\n|Self Employed)',
        'self_employed': r'Self Employed\s*:\s*(Yes|No)',
        'no_of_dependents': r'Number of Dependents\s*:\s*(\d+)',
        'income_annum': r'Annual Income\s*:\s*₹?([\d,]+)',
        'loan_amount': r'Loan Amount Requested\s*:\s*₹?([\d,]+)',
        'loan_term': r'Loan Term\s*:\s*(\d+)\s*years?',
        'cibil_score': r'CIBIL Score\s*:\s*(\d+)',
        'residential_assets': r'Residential Assets\s*:\s*₹?([\d,]+)',
        'commercial_assets': r'Commercial Assets\s*:\s*₹?([\d,]+)',
        'luxury_assets': r'Luxury Assets\s*:\s*₹?([\d,]+)',
        'bank_assets': r'Bank Assets\s*:\s*₹?([\d,]+)'
    }
    
    extracted = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted[field] = match.group(1).strip()
    
    # Clean numeric fields
    for field in ['income_annum', 'loan_amount', 'residential_assets',
                 'commercial_assets', 'luxury_assets', 'bank_assets']:
        if field in extracted:
            extracted[field] = extracted[field].replace(',', '')
    
    return extracted

def process_document(file_path: str) -> Dict[str, str]:
    """Process PDF or image document"""
    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path)
        full_text = ""
        for img in images:
            full_text += extract_text_from_image(np.array(img)) + "\n"
    else:
        full_text = extract_text_from_image(file_path)
    
    return extract_loan_fields(full_text)