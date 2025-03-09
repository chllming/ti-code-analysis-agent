#!/usr/bin/env python3
"""
Script to create a clean Python file with proper line endings.
"""

with open('perfect_code.py', 'w') as f:
    f.write('''#!/usr/bin/env python3
"""
Example of clean Python code that follows PEP 8 guidelines.
"""


def good_function():
    """Calculate and display a simple calculation."""
    x = 1 + 2  # Simple addition with proper spacing
    if x > 5:
        print("Value is greater than 5")
        return True
    else:
        y = [1, 2, 3, 4, 5]
        print(f"First element: {y[0]}")
        return False


if __name__ == "__main__":
    result = good_function()
    print(f"Function returned: {result}")
''') 