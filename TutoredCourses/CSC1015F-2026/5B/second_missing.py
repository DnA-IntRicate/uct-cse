# Adam Foflonker
# Assignment 5B sample solution
# 01/04/2026


numbers = list(map(int, input("Enter a sequence of space-separated numbers:\n").strip().split()))
missing = [x for a, b in zip(numbers, numbers[1:]) for x in range(a + 1, b)]

if not missing or len(missing) > 2:
    print("Error: Expected exactly two missing numbers.")
    exit()

print(f"Missing numbers: {str(missing)[1:-1]}")
