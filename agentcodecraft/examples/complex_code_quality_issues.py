"""
Complex code with multiple code quality issues.
This code demonstrates various anti-patterns that should be refactored.
"""

# Code Quality Issue 1: Global variables
global_counter = 0
global_data = []

# Code Quality Issue 2: Bare except clauses
def risky_operation(data):
    try:
        result = data / 0
        return result
    except:  # Bare except - bad practice
        return None

# Code Quality Issue 3: String concatenation in loop
def build_message(items):
    """Inefficient: String concatenation in loop."""
    message = ""
    for item in items:
        message += str(item) + ", "  # Should use join()
    return message

# Code Quality Issue 4: Using map() instead of list comprehension
def process_numbers(numbers):
    """Less readable: Using map() instead of list comprehension."""
    doubled = list(map(lambda x: x * 2, numbers))
    return doubled

# Code Quality Issue 5: Using .format() instead of f-strings
def greet_user(name, age):
    """Old-style formatting."""
    message = "Hello, {}! You are {} years old.".format(name, age)
    return message

# Code Quality Issue 6: Print statements instead of logging
def debug_function(value):
    print("Debug: Processing value:", value)
    print("Debug: Value type:", type(value))
    return value * 2

# Code Quality Issue 7: Long function (exceeds 50 lines conceptually)
def complex_function(data):
    """This function does too many things."""
    # Step 1: Validate input
    if not data:
        return None
    
    # Step 2: Process data
    processed = []
    for item in data:
        if item > 0:
            processed.append(item * 2)
        else:
            processed.append(0)
    
    # Step 3: Filter data
    filtered = []
    for item in processed:
        if item > 10:
            filtered.append(item)
    
    # Step 4: Sort data
    filtered.sort()
    
    # Step 5: Calculate statistics
    total = sum(filtered)
    average = total / len(filtered) if filtered else 0
    
    # Step 6: Format output
    output = {
        "total": total,
        "average": average,
        "count": len(filtered),
        "items": filtered
    }
    
    # Step 7: Log results
    print("Results:", output)
    
    return output

# Example usage
if __name__ == "__main__":
    items = ["apple", "banana", "cherry"]
    print(build_message(items))
    
    numbers = [1, 2, 3, 4, 5]
    print(process_numbers(numbers))
    
    print(greet_user("Alice", 30))
    
    debug_function(42)
    
    data = [1, 2, 3, -1, 5, 6, 7, 8, 9, 10]
    result = complex_function(data)
    print(result)

