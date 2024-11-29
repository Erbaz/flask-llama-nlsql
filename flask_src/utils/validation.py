
def validate_request_data(data):
    # Initialize an empty list to collect errors
    errors = [f"Item at index {index} is missing or empty." for index, value in enumerate(data) if not value]

    if errors:
        return False

    # If all is valid, return true
    return True
