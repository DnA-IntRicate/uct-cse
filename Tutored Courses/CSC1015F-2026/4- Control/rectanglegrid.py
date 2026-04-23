# Adam Foflonker
# 19/03/2026


start: int = 0
row: int = 0
col: int = 0

while True:
    try:
        start = int(input("Enter the starting number (n):\n"))
        row = int(input("Enter the number of rows (r):\n"))
        col = int(input("Enter the number of columns (c):\n"))
    except ValueError:
        print("Invalid input. Please enter integers.")
        continue

    if (row < 0) or (col < 0):
        print("Rows and columns must be positive integers.")
        continue

    break

for i in range(row):
    for j in range(col):
        print(str(start).rjust(3), end = " ")
        start += 1

    print()
