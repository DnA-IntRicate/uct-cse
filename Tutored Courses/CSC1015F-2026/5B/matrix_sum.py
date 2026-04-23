# Adam Foflonker
# Assignment 5B sample solution
# 01/04/2026


print("Enter 4 rows (each 4 digits, e.g., 2941):")
mat = [list(map(int, input().strip())) for _ in range(4)]

while True:
    row, col = (map(int, input("Enter coordinates: ").strip().split()))
    if (row == -1) and (col == -1):
        break

    print(f"Row sum = {sum(mat[row])}")
    print(f"Column sum = {sum(r[col] for r in mat)}")
