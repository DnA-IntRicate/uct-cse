# Adam Foflonker
# 19/03/2026


num: int = 0
try:
    num = int(input("Enter a non-negative integer:\n"))
except ValueError:
    print("Invalid input. Please enter a valid integer.")
    exit()

if num < 0:
    print("Please enter a non-negative integer.")
    exit()

for _ in range(25):
    print(num, end = " ")

    rev = 0
    temp = num
    while temp > 0:
        digit = temp % 10
        temp //= 10
        rev = (rev * 10) + digit

    if num == rev:
        exit()

    num += rev

print("\nNo palindrome found in 25 iterations.")
