# Assignment 4
# armstrong.py Sample Solution
# Adam Foflonker (FFLADA001)
# 13/03/25

userIn = input("Enter a number:\n")
if not userIn.isdigit():
    print("Invalid input.")
    exit()

num = int(userIn)
power = len(userIn)
armstrong = 0

while num > 0:
    armstrong += (num % 10) ** power
    num = num // 10

if armstrong == int(userIn):
    print(f"{userIn} is an Armstrong number.")
else:
    print(f"{userIn} is not an Armstrong number.")

