# Assignment 5
# duplicates.py Sample Solution
# Adam Foflonker (FFLADA001)
# 03/04/25

print("Unique element array:", list(dict.fromkeys(map(int, input("Enter an array of numbers (separated by spaces):\n").split()))))

# 20 2 9 20 6 7 8 9 2 20 9 6 7
# Unique element array: [20, 2, 9, 6, 7, 8]
