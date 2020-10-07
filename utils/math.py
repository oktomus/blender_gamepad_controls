
def map_float(min_input, max_input, min_output, max_output, value):
    """Map a value from one range to another."""
    return min_output + (max_output - min_output) * (value - min_input) / (max_input - min_input)

def clamp(value, low, high):
    """Clamp the given value in the given range."""
    return max(low, min(high, value))