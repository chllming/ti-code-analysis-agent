import sys
import os
import json  # Unused import

def calculate_something(a,b):  # Missing whitespace after comma
    x=a+b  # Missing whitespace around operators
    y= a*b  # Inconsistent spacing
    
    if x>10:  # Missing whitespace around comparison
       return y+100  # Incorrect indentation (3 spaces instead of 4)
    else:
        return x   # Trailing whitespace
    
    # Unreachable code
    print("This will never run")

# Line that's too long - should trigger line length warning if using default settings
very_long_variable_name = "This is a very long string that will likely exceed the default line length limit set by Flake8"

class SampleClass:  # Missing docstring
    def __init__(self):
        self.value = 42
        
    def some_method(self):  # Missing docstring
        x = 10
        # Unused variable
        unused_var = "I'm never used"
        return x+self.value  # Missing whitespace 