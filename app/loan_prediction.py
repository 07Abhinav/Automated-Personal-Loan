import joblib
import pandas as pd
import numpy as np
import re
from pathlib import Path
from typing import Dict

class LoanPredictor:
    def __init__(self):
        # Model paths
        self.models_path = Path("E:/TCS project/Automated-Personal-Loan/models")
        
        # Load trained artifacts
        self.model = joblib.load(self.models_path / "loan_approval_model.pkl")
        self.scaler = joblib.load(self.models_path / "scaler.pkl")
        self.label_encoders = joblib.load(self.models_path / "label_encoders.pkl")
        
        # Get exact feature order from model or define manually
        if hasattr(self.model, 'feature_names_in_'):
            self.feature_order = self.model.feature_names_in_
        else:
            # Define feature order manually if not available
            self.feature_order = [
                'no_of_dependents', 'education', 'self_employed', 'income_annum',
                'loan_amount', 'loan_term', 'cibil_score', 'residential_assets_value',
                'commercial_assets_value', 'luxury_assets_value', 'bank_asset_value', 'address'
            ]
        
        # Define expected schema based on your CSV
        self.expected_features = [
            'education', 'self_employed', 'no_of_dependents', 'income_annum',
            'loan_amount', 'loan_term', 'cibil_score', 'residential_assets_value',
            'commercial_assets_value', 'luxury_assets_value', 'bank_asset_value', 'address'
        ]
        
        # Categorical mappings from your notebook
        self.categorical_map = {
            'education': ['Graduate', 'Not Graduate'],
            'self_employed': ['No', 'Yes'],
            'address': ['america', 'australia', 'dubai', 'india', 'japan']
        }
        print("Expected feature order:", self.feature_order)

    def _clean_numeric(self, value):
        """Convert string numbers with symbols to float"""
        if isinstance(value, str):
            return float(re.sub(r'[^\d.]', '', value))
        return float(value)

    def preprocess_input(self, extracted_data: Dict) -> pd.DataFrame:
        """Transform raw data to model-ready format"""
        # Initialize with correct column order
        processed = pd.DataFrame(columns=self.feature_order)
        
        # 1. Process numeric fields
        numeric_fields = [
            'no_of_dependents', 'income_annum', 'loan_amount', 'loan_term',
            'cibil_score', 'residential_assets_value', 'commercial_assets_value',
            'luxury_assets_value', 'bank_asset_value'
        ]
        
        for field in numeric_fields:
            if field in self.feature_order:
                processed[field] = [self._clean_numeric(extracted_data.get(field, 0))]
        
        # 2. Process categorical fields
        for field, allowed_values in self.categorical_map.items():
            if field in self.feature_order:
                raw_value = str(extracted_data.get(field, '')).strip()
                if raw_value in allowed_values:
                    encoded = self.label_encoders[field].transform([raw_value])[0]
                else:
                    encoded = 0  # Default to first category
                processed[field] = [encoded]
        
        # 3. Handle missing features
        for feature in self.feature_order:
            if feature not in processed.columns:
                processed[feature] = 0  # Default value for missing features
        
        # Debugging: Print the preprocessed DataFrame
        print("Preprocessed DataFrame:", processed)
        
        return processed[self.feature_order]

    def predict(self, extracted_data: Dict) -> Dict:
        """Make prediction with full validation"""
        try:
            # Validate and preprocess
            input_df = self.preprocess_input(extracted_data)
            
            # Verify feature match
            if list(input_df.columns) != list(self.feature_order):
                missing = set(self.feature_order) - set(input_df.columns)
                extra = set(input_df.columns) - set(self.feature_order)
                raise ValueError(
                    f"Feature mismatch. Missing: {missing}. Extra: {extra}. "
                    f"Expected order: {self.feature_order}"
                )
            
            # Transform and predict
            scaled = self.scaler.transform(input_df)
            pred = self.model.predict(scaled)[0]
            proba = self.model.predict_proba(scaled)[0][1]
            
            return {
                'status': self.label_encoders['loan_status'].inverse_transform([pred])[0],
                'approval_probability': float(proba),
                'risk_factors': self._identify_risk_factors(input_df.iloc[0])
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'Error',
                'approval_probability': 0.0
            }

    def _identify_risk_factors(self, row) -> list:
        """Explain model decision based on key factors"""
        risks = []
        
        # CIBIL Score check
        if row['cibil_score'] < 600:
            risks.append(f"Low CIBIL score ({row['cibil_score']})")
        
        # Debt-to-income ratio
        if row['loan_amount'] > 3 * row['income_annum']:
            ratio = row['loan_amount'] / max(1, row['income_annum'])
            risks.append(f"High debt-to-income ratio ({ratio:.1f}x)")
        
        # Self-employed risk
        if row['self_employed'] == 1:  # Encoded 'Yes'
            risks.append("Self-employed applicant")
            
        return risks if risks else ["All criteria met"]