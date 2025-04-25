## 🏗️ Installation
### Prerequisites
- Python 3.8+
- Tesseract OCR ([Install Guide](https://github.com/tesseract-ocr/tesseract))
- Poppler (for PDF→image conversion)

### Steps
1. Clone the repo:
   ```bash
   git clone https://github.com/your-repo/loan-processing-system.git
   cd loan-processing-system
   ```

2. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```

## Start the app

# Comprehensive Report: Automated Personal Loan Document Processing System  

## 1. Introduction  
The Automated Personal Loan Document Processing System leverages Optical Character Recognition (OCR) and Machine Learning (ML) to streamline loan application processing. This report details the methodology, implementation, results, and conclusions of the project, along with the rationale behind the selected approach.

---

## 2. Methodology  

### 2.1 System Architecture  
The system follows a three-stage pipeline:  

1. Document Processing & OCR  
   - Input: PDF/Image loan applications  
   - OCR Engine: Tesseract OCR  
   - Preprocessing: Noise reduction, contrast adjustment, and text enhancement  

2. Data Extraction & Validation  
   - Key Fields: Name, income, loan amount, CIBIL score, assets  
   - Validation Rules:  
     - Numeric range checks (e.g., CIBIL score ≥ 300)  
     - Mandatory field checks  

3. Loan Approval Prediction (ML Model)  
   - Model: Random Forest Classifier  
   - Features: Income, loan amount, CIBIL score, employment status  
   - Output: Approval/Rejection with probability score  

### 2.2 Technical Stack  
| Component          | Technology Used          |
|--------------------|--------------------------|
| OCR            | Tesseract OCR (pytesseract) |
| ML Framework   | Scikit-learn (Random Forest) |
| Backend        | Python (Streamlit)       |
| Data Processing| OpenCV, Pandas           |

---

## 3. Implementation  

### 3.1 Data Collection & Preprocessing  
- Dataset: `loan_approval_dataset.csv` containing:  
  - Features: `income_annum`, `loan_amount`, `cibil_score`, etc.  
  - Target: `loan_status` (Approved/Rejected)  

- Preprocessing Steps:  
  - Missing Value Handling: Dropped rows with missing data  
  - Categorical Encoding: Label Encoding (`education`, `self_employed`)  
  - Feature Scaling: StandardScaler applied  

### 3.2 Machine Learning Model  
- Algorithm: Random Forest Classifier  
  - Why Random Forest?  
    - Handles non-linear relationships well  
    - Robust to outliers  
    - Provides feature importance scores  
  - Performance Metrics:  
    | Metric          | Value   |
    |----------------|---------|
    | Accuracy    | 97.6%   |
    | Precision   | 0.98    |
    | Recall      | 0.98    |
    | F1-Score    | 0.98    |

### 3.3 OCR & Data Extraction  
- Key Challenges & Solutions:  
  | Challenge                          | Solution Implemented               |
  |------------------------------------|------------------------------------|
  | Inconsistent document formats  | Regex-based field extraction       |
  | Poor scan quality              | OpenCV preprocessing (thresholding, noise removal) |
  | Missing fields                 | Default value imputation           |

---

## 4. Results  

### 4.1 OCR Accuracy  
- Extraction Success Rate: ~90%  
- Common Errors:  
  - Merged fields (e.g., "Address" and "Date of Birth")  
  - Incorrect numeric parsing (e.g., ₹5,00,000 → 500000)  

### 4.2 Loan Approval Prediction  
```bash
- Test Case Results:  

| Scenario                | Prediction | Confidence | Key Factors Considered |
|------------------------|------------|------------|------------------------|
| High CIBIL (750), Low Debt | ✅ Approved | 92% | Strong credit score |
| Low CIBIL (350), High Loan | ❌ Rejected | 15% | High debt-to-income ratio |
| Self-Employed Applicant | ❌ Rejected | 28% | Employment risk |
```

### 4.3 System Performance  
- Processing Time:  
  - PDF → Extraction: ~2-3 sec/page  
  - Prediction: < 1 sec  

---

## 5. Conclusions  

### 5.1 Why This Approach Was Selected  
1. OCR + ML Combination:  
   - Traditional rule-based systems fail with unstructured documents.  
   - Tesseract OCR + Regex ensures flexible text extraction.  

2. Random Forest Over Alternatives:  
   - Compared to Logistic Regression, it handles non-linear patterns better.  
   - More interpretable than Neural Networks for regulatory compliance.  

3. Streamlit for UI:  
   - Rapid prototyping for bank employees.  
   - Easy integration with Python backend.  

### 5.2 Limitations & Future Work  
| Limitation               | Proposed Improvement          |
|-----------------------------|----------------------------------|
| Handwritten text support| Integrate Google Vision API  |
| Multi-language support  | Add language detection       |
| Real-time bank integration | API connection to core banking systems |

---

## 6. Final Recommendation  
The implemented system:  
✅ Reduces manual processing time by ~70%  
✅ Achieves 97.6% prediction accuracy  
✅ Provides explainable decisions (risk factors)  


---

```bash
### Appendix: Code & Demo  
- GitHub Repo: https://github.com/07Abhinav/Automated-Personal-Loan
- Demo Video: https://drive.google.com/file/d/1QMfAnxZf-JXX4s3tMDKahmytKnthfsl3/view?usp=sharing
```

---

This report summarizes the end-to-end automated loan processing system, highlighting its effectiveness in reducing manual effort while maintaining high accuracy. 🚀