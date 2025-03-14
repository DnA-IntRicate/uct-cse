# Assignment 4
# rectanglegrid.py Sample Solution
# Adam Foflonker (FFLADA001)
# 13/03/25

start = int(input("Enter the starting number (n):\n"))
rows = int(input("Enter the number of rows (r):\n"))
cols = int(input("Enter the number of columns (c):\n"))

if (rows <= 0) or (cols <= 0):
    print("Rows and columns must be positive integers.")
    exit()

for i in range(rows):
    for j in range(cols):
        print(f"{start:3}", end=" ")
        start += 1

    print()
