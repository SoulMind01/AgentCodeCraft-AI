"""
Code with performance issues that should be optimized.
"""

# Performance Issue 1: String concatenation in loop
def build_csv_row_inefficient(items):
    """Inefficient: O(n²) string concatenation."""
    row = ""
    for item in items:
        row += str(item) + ","  # Should use join()
    return row.rstrip(",")

# Performance Issue 2: Using map() instead of list comprehension
def square_numbers_inefficient(numbers):
    """Less efficient and less readable."""
    squared = list(map(lambda x: x * 2, numbers))  # Should use [x*2 for x in numbers]
    return squared

# Performance Issue 3: Using filter() instead of list comprehension
def get_positive_numbers_inefficient(numbers):
    """Less efficient and less readable."""
    positive = list(filter(lambda x: x > 0, numbers))  # Should use [x for x in numbers if x > 0]
    return positive

# Performance Issue 4: Repeated calculations in loop
def calculate_distances_inefficient(points, center):
    """Inefficient: Recalculates center coordinates in each iteration."""
    distances = []
    for point in points:
        # These calculations happen every iteration
        center_x, center_y = center[0], center[1]  # Should be outside loop
        distance = ((point[0] - center_x) ** 2 + (point[1] - center_y) ** 2) ** 0.5
        distances.append(distance)
    return distances

# Performance Issue 5: Creating large lists when generators would suffice
def process_large_dataset_inefficient(data):
    """Inefficient: Creates full list in memory."""
    # This creates a full list even if we only need to iterate once
    processed = [x * 2 for x in data if x > 0]  # Could use generator: (x*2 for x in data if x > 0)
    total = sum(processed)
    return total

# Performance Issue 6: Multiple string concatenations
def build_message_inefficient(parts):
    """Inefficient: Multiple string concatenations."""
    message = ""
    message += "Header: "
    for part in parts:
        message += part + " | "  # Should use join()
    message += "Footer"
    return message

# Example usage
if __name__ == "__main__":
    # Test string concatenation
    items = ["apple", "banana", "cherry", "date", "elderberry"]
    csv_row = build_csv_row_inefficient(items)
    print("CSV Row:", csv_row)
    
    # Test map/filter
    numbers = [1, 2, 3, 4, 5, -1, -2, 6, 7, 8]
    squared = square_numbers_inefficient(numbers)
    print("Squared:", squared)
    
    positive = get_positive_numbers_inefficient(numbers)
    print("Positive:", positive)
    
    # Test repeated calculations
    points = [(1, 2), (3, 4), (5, 6), (7, 8)]
    center = (0, 0)
    distances = calculate_distances_inefficient(points, center)
    print("Distances:", distances)
    
    # Test large dataset processing
    large_data = list(range(1000))
    total = process_large_dataset_inefficient(large_data)
    print("Total:", total)
    
    # Test message building
    parts = ["Part1", "Part2", "Part3", "Part4"]
    message = build_message_inefficient(parts)
    print("Message:", message)

