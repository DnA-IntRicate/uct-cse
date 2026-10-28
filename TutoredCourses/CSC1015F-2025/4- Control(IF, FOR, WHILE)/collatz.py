# Assignment 4
# collatz.py Sample Solution
# Adam Foflonker (FFLADA001)
# 13/03/25

num = input("Enter a positive integer:\n")
if not num.isdigit():
    print("Invalid input.")
    exit()

num = int(num)
if num <= 0:
    print("Please enter a positive integer.")
    exit()

while num > 1:
    if num % 2 == 0:
        num = num // 2
    else:
        num = (num * 3) + 1

    print(num, end=" ")

print()
