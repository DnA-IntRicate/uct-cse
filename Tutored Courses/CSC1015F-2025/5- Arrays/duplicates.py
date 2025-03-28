# A program to remove duplicates from an array and print the modified array
# Lebeko Poulo
# 19/03/2025

arr = list(map(int, input("Enter an array of numbers (separated by spaces):\n").split()))  # Take input

seen = set()  # Set to track unique elements
unique_arr = []  # List to store non-duplicate elements

for num in arr:
    if num not in seen:  # Add only if not already seen
        seen.add(num)
        unique_arr.append(num)

print("Unique element array:", unique_arr)
