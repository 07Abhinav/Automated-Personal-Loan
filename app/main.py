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
from loan_prediction import LoanPredictor  # Our new prediction class
import pytesseract
import cv2
from PIL import Image

# Initialize loan predictor
# predictor = LoanPredictor()
from loan_prediction import LoanPredictor

# Initialize predictor
predictor = LoanPredictor()

def show_decision(data):
    """Display loan decision results"""
    result = predictor.predict(data)
    
    if 'error' in result:
        st.error(f"Prediction Error: {result['error']}")
        st.write("Required features:", predictor.expected_features)
        return
    
    # Display decision
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Decision")
        if result['status'] == "Approved":
            st.success(f"✅ {result['status']}")
        else:
            st.error(f"❌ {result['status']}")
        
        st.metric("Approval Probability", 
                 f"{result['approval_probability']:.1%}")
    
    with col2:
        st.subheader("Key Factors")
        for factor in result['risk_factors']:
            st.write(f"- {factor}")
    
    # Show technical details
    with st.expander("Technical Details"):
        st.write("Features used for prediction:")
        st.json({k: data.get(k, "MISSING") for k in predictor.expected_features})

# Create directories if they don't exist
Path(RAW_DOCS_DIR).mkdir(parents=True, exist_ok=True)
Path(PROCESSED_DIR).mkdir(parents=True, exist_ok=True)

# Set page config
st.set_page_config(page_title="Loan Document Processor", layout="wide")

# Title
st.title("Automated Personal Loan Document Processing")

def show_prediction_results(data):
    """Display loan approval prediction results"""
    st.subheader("Loan Approval Prediction")
    
    result = predictor.predict(data)
    
    if 'error' in result:
        st.error(f"Prediction error: {result['error']}")
        st.write("Model expects these features in order:")
        st.write(result.get('features_used', []))
        return
    
    # Display results
    col1, col2 = st.columns(2)
    with col1:
        if result['status'] == "Approved":
            st.success(f"✅ {result['status']}")
        else:
            st.error(f"❌ {result['status']}")
        
        st.metric("Dispproval Probability", 
                 f"{result['approval_probability']:.2%}")
    
    with col2:
        st.write("**Decision Reason:**")
        st.info(result.get('decision_reason', 'No reason provided'))
    
    # Show detailed risk factors if available
    if 'risk_factors' in result and result['risk_factors']:
        with st.expander("Detailed Risk Factors"):
            for factor in result['risk_factors']:
                st.write(f"- {factor}")
    
    # Debug info
    with st.expander("Technical Details"):
        st.write("**Features Used:**")
        if 'features_used' in result:
            st.json({col: data.get(col, "MISSING") for col in result['features_used']})
        else:
            st.warning("No feature details available.")

# File upload
uploaded_file = st.file_uploader("Upload Loan Document", type=['pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Save the uploaded file
    file_path = os.path.join(RAW_DOCS_DIR, uploaded_file.name)
    
    # Handle duplicate filenames
    counter = 1
    while os.path.exists(file_path):
        name, ext = os.path.splitext(uploaded_file.name)
        file_path = os.path.join(RAW_DOCS_DIR, f"{name}_{counter}{ext}")
        counter += 1
    
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
            try:
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
                
                # Store extracted data in session state
                st.session_state['extracted_data'] = extracted_data
                
                # Show prediction immediately if no errors
                if not validation_errors:
                    show_prediction_results(extracted_data)
                    
            except Exception as e:
                st.error(f"Processing failed: {str(e)}")
    
    # Manual correction section
    if 'extracted_data' in st.session_state:
        st.subheader("Manual Correction")
        corrected_data = {}
        for field, value in st.session_state['extracted_data'].items():
            corrected_data[field] = st.text_input(field, value)
        
        if st.button("Save Corrections"):
            st.session_state['corrected_data'] = corrected_data
            st.success("Corrections saved!")
            
            # Show updated prediction
            show_prediction_results(corrected_data)
    
    # Final submission
    if st.button("Submit to Loan Processing System"):
        data_to_send = st.session_state.get('corrected_data', 
                                          st.session_state.get('extracted_data', {}))
        
        if data_to_send:
            # Here you would normally call your API or database integration
            st.success(f"Loan application submitted successfully!")
            st.balloons()
            
            # Show final decision
            show_prediction_results(data_to_send)
        else:
            st.warning("Please process the document first")

