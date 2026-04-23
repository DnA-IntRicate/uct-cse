# Adam Foflonker
# 19/03/2026


num: int = 0
try:
    num = int(input("Enter a positive integer:\n"))
except ValueError:
    print("Invalid input. Please enter a valid integer.")
    exit()

if num < 0:
    print("Please enter a positive integer.")
    exit()

print(f"{num} produces the sequence:")
print(num, end = " ")

while num > 10:
    prod = 1
    temp = num
    while temp > 0:
        prod *= temp % 10
        temp //= 10

    print(prod, end = " ")
    num = prod
