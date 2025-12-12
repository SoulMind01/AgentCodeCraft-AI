"""
Complex code with multiple security violations.
This code demonstrates various security anti-patterns that should be refactored.
"""

# Security Violation 1: Hardcoded credentials
api_key = "sk_live_1234567890abcdef"
password = "admin123"
secret_token = "my_secret_token_here"

# Security Violation 2: Using eval() for dynamic code execution
def calculate_expression(expr):
    """Dangerous: Uses eval() to evaluate expressions."""
    result = eval(expr)
    return result

# Security Violation 3: Using exec() for dynamic code
def execute_user_code(user_code):
    """Dangerous: Executes arbitrary user code."""
    exec(user_code)
    return "Code executed"

# Security Violation 4: Unsafe deserialization
import pickle

def load_user_data(data):
    """Dangerous: Uses pickle.loads() with potentially untrusted data."""
    return pickle.loads(data)

# Example usage (would trigger violations)
if __name__ == "__main__":
    # These would all trigger security violations
    calculate_expression("2 + 2")
    execute_user_code("print('Hello')")
    load_user_data(b"some_pickled_data")

