import streamlit as st
import pandas as pd
import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from src.ocr_processing import process_document
from src.data_validation import validate_extracted_data
from src.config import RAW_DOCS_DIR, PROCESSED_DIR
from src.preprocessing import convert_pdf_to_images, preprocess_image
import pytesseract
import cv2
from PIL import Image

# Create directories if they don't exist
Path(RAW_DOCS_DIR).mkdir(parents=True, exist_ok=True)
Path(PROCESSED_DIR).mkdir(parents=True, exist_ok=True)

# Set page config
st.set_page_config(page_title="Loan Document Processor", layout="wide")

# Title
st.title("Automated Personal Loan Document Processing")

# File upload
uploaded_file = st.file_uploader("Upload Loan Document", type=['pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Save the uploaded file
    file_path = os.path.join(RAW_DOCS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Display document preview
    st.subheader("Document Preview")
    if uploaded_file.type == "application/pdf":
        images = convert_pdf_to_images(file_path)
        st.image(images[0], caption="First page of PDF", use_column_width=True)
    else:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)
    
    # Process document
    if st.button("Process Document"):
        with st.spinner("Processing document..."):
            # Extract data
            extracted_data = process_document(file_path)
            
            # Validate data
            validation_errors = validate_extracted_data(extracted_data)
            
            # Display results
            st.subheader("Extracted Data")
            df = pd.DataFrame.from_dict(extracted_data, orient='index', columns=['Value'])
            st.dataframe(df)
            
            if validation_errors:
                st.subheader("Validation Errors")
                st.error("\n".join([f"{k}: {v}" for k, v in validation_errors.items()]))
            else:
                st.success("All extracted data passed validation checks!")
                
            # Allow manual correction
            st.subheader("Manual Correction")
            corrected_data = {}
            for field, value in extracted_data.items():
                corrected_data[field] = st.text_input(field, value)
            
            if st.button("Save Corrections"):
                st.session_state['corrected_data'] = corrected_data
                st.success("Corrections saved!")
                
            # Integration option
            if st.button("Send to Loan Processing System"):
                if 'corrected_data' in st.session_state:
                    data_to_send = st.session_state['corrected_data']
                else:
                    data_to_send = extracted_data
                
                # Here you would normally call your API or database integration
                st.success(f"Data for loan ID {data_to_send.get('loan_id', 'N/A')} sent to processing system!")