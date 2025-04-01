from utils import validate_input, transform_data

def process_data(data):
    """Process input data and return results"""
    # Validate input
    if not validate_input(data):
        raise ValueError("Invalid input data")
    
    # Transform data
    result = transform_data(data)
    return result

def main():
    data = [1, 2, 3]
    result = process_data(data)
    print(f"Processed result: {result}") 