"""
Realistic production-like code with mixed violations.
This simulates actual code that might need refactoring in a real project.
"""

import os
import sys

# Security: Hardcoded credentials
DATABASE_PASSWORD = "production_password_123"
API_SECRET = "sk_live_abc123xyz789"

# Code Quality: Global state
user_sessions = {}
request_count = 0

class DataProcessor:
    """A class that processes user data with various issues."""
    
    def __init__(self):
        self.data = []
        self.errors = []
    
    def process_user_input(self, user_input):
        """Process user input with potential security issues."""
        try:
            # Security: Using eval() for user input
            result = eval(user_input)
            return result
        except:  # Code Quality: Bare except
            self.errors.append("Invalid input")
            return None
    
    def build_error_message(self, errors):
        """Code Quality: Inefficient string building."""
        message = "Errors: "
        for error in errors:
            message += error + "; "  # Should use join()
        return message
    
    def format_user_info(self, name, email, age):
        """Style: Using .format() instead of f-strings."""
        info = "User: {} ({}) - Age: {}".format(name, email, age)
        return info
    
    def log_debug_info(self, data):
        """Style: Using print() instead of logging."""
        print("DEBUG: Processing data:", data)
        print("DEBUG: Data length:", len(data))
        print("DEBUG: Data type:", type(data))
    
    def filter_and_transform(self, items):
        """Code Quality: Using map/filter instead of comprehensions."""
        # Filter positive numbers
        positive = list(filter(lambda x: x > 0, items))
        # Double them
        doubled = list(map(lambda x: x * 2, positive))
        return doubled
    
    def unsafe_deserialize(self, serialized_data):
        """Security: Unsafe deserialization."""
        import pickle
        return pickle.loads(serialized_data)
    
    def execute_dynamic_code(self, code_string):
        """Security: Using exec() for dynamic code."""
        exec(code_string)
        return "Code executed"

def authenticate_user(username, password):
    """Authentication function with security issues."""
    # Security: Hardcoded password check
    if password == "admin123":
        return True
    
    # Code Quality: Global variable usage
    global user_sessions
    user_sessions[username] = True
    global request_count
    request_count += 1
    
    return False

def process_batch_data(data_batch):
    """Process a batch of data with various issues."""
    results = []
    
    for item in data_batch:
        try:
            # Style: Using print for debugging
            print("Processing item:", item)
            
            # Code Quality: String concatenation
            status = "Processing: "
            status += str(item) + " - "
            status += "Status: OK"
            
            results.append(status)
        except:  # Code Quality: Bare except
            print("Error processing item")
    
    # Style: Using .format()
    summary = "Processed {} items successfully".format(len(results))
    print(summary)
    
    return results

# Main execution
if __name__ == "__main__":
    processor = DataProcessor()
    
    # Test with various inputs
    user_input = "2 + 2"
    result = processor.process_user_input(user_input)
    print("Result:", result)
    
    # Test string building
    errors = ["Error 1", "Error 2", "Error 3"]
    error_msg = processor.build_error_message(errors)
    print(error_msg)
    
    # Test formatting
    user_info = processor.format_user_info("John Doe", "john@example.com", 30)
    print(user_info)
    
    # Test filtering
    numbers = [-2, -1, 0, 1, 2, 3, 4, 5]
    filtered = processor.filter_and_transform(numbers)
    print("Filtered and doubled:", filtered)
    
    # Test batch processing
    batch = [1, 2, 3, "invalid", 5]
    batch_results = process_batch_data(batch)
    print("Batch results:", batch_results)

