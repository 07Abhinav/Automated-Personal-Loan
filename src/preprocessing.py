import cv2
import numpy as np
import os
from PIL import Image
from pdf2image import convert_from_path
from .config import RAW_DOCS_DIR, PROCESSED_DIR

def preprocess_image(image_path):
    """
    Preprocess image for better OCR results
    """
    try:
        # Read image - handle both file paths and PIL images
        if isinstance(image_path, str):
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image at {image_path}")
        else:  # Assume it's a PIL Image
            img = np.array(image_path)
            # Convert RGB to BGR for OpenCV
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Rest of your processing...
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(cleaned)
        
        return enhanced
    except Exception as e:
        print(f"Error preprocessing image: {str(e)}")
        raise

def convert_pdf_to_images(pdf_path):
    """
    Convert PDF to images
    """
    images = convert_from_path(pdf_path)
    return images

def save_processed_image(image, filename):
    """
    Save processed image
    """
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
    
    save_path = os.path.join(PROCESSED_DIR, filename)
    cv2.imwrite(save_path, image)
    return save_path