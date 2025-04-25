from .config import VALIDATION_RULES

def validate_extracted_data(data):
    """
    Validate the extracted data against business rules
    """
    errors = {}
    
    for field, value in data.items():
        if field in VALIDATION_RULES:
            rules = VALIDATION_RULES[field]
            
            # Check numeric fields
            if 'min_value' in rules or 'max_value' in rules:
                try:
                    num_value = float(str(value).replace(',', '').replace('$', ''))
                    if 'min_value' in rules and num_value < rules['min_value']:
                        errors[field] = f"Value too small (min {rules['min_value']})"
                    if 'max_value' in rules and num_value > rules['max_value']:
                        errors[field] = f"Value too large (max {rules['max_value']})"
                except ValueError:
                    errors[field] = "Invalid numeric format"
            
            # Check string length
            if 'min_length' in rules and len(str(value)) < rules['min_length']:
                errors[field] = f"Too short (min {rules['min_length']} chars)"
            if 'max_length' in rules and len(str(value)) > rules['max_length']:
                errors[field] = f"Too long (max {rules['max_length']} chars)"
            
            # Check pattern
            if 'pattern' in rules and not re.match(rules['pattern'], str(value)):
                errors[field] = "Invalid format"
    
    return errors if errors else None