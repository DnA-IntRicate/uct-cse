# Find the missing number from an array
# Lebeko Poulo
# 19/03/2025

arr = list(map(int, input("Enter an array of numbers (separated by spaces):\n").split()))  # Take input

min_val = min(arr)  # Find the smallest number in the sequence
max_val = max(arr)  # Find the largest number in the sequence

expected_sum = sum(range(min_val, max_val + 1))  # Sum of all numbers in the expected range
actual_sum = sum(arr)  # Sum of given numbers

missing_number = expected_sum - actual_sum  # Compute the missing number

if missing_number != 0:
    print("Missing number:", missing_number)
else:
    print("There is no missing number.")
    