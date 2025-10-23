# Simple calculator - needs brownfield transformation

def calculate(operation, num1, num2):
    # High complexity function
    if operation == "add":
        result = num1 + num2
    elif operation == "subtract":
        result = num1 - num2
    elif operation == "multiply":
        result = num1 * num2
    elif operation == "divide":
        if num2 == 0:
            print("Error: Division by zero")
            return None
        result = num1 / num2
    elif operation == "power":
        result = num1 ** num2
    elif operation == "modulo":
        result = num1 % num2
    else:
        print(f"Unknown operation: {operation}")
        return None
    return result

def advanced_calculate(operation, numbers):
    # Even higher complexity
    if operation == "sum":
        total = 0
        for n in numbers:
            total = total + n
        return total
    elif operation == "product":
        total = 1
        for n in numbers:
            total = total * n
        return total
    elif operation == "average":
        if len(numbers) == 0:
            return 0
        total = 0
        for n in numbers:
            total = total + n
        return total / len(numbers)
    elif operation == "max":
        if len(numbers) == 0:
            return None
        max_val = numbers[0]
        for n in numbers:
            if n > max_val:
                max_val = n
        return max_val
    else:
        print(f"Unknown operation: {operation}")
        return None

# Main execution (no if __name__ == "__main__")
print("Calculator v1.0")
print("Result:", calculate("add", 5, 3))
print("Sum:", advanced_calculate("sum", [1, 2, 3, 4, 5]))
