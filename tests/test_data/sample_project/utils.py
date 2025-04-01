def validate_input(data):
    """Validate input data"""
    return isinstance(data, list) and all(isinstance(x, (int, float)) for x in data)

def transform_data(data):
    """Transform input data"""
    return [x * 2 for x in data] 