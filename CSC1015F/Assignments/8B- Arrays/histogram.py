# Adam Foflonker
# FFLADA001
# 12/04/24
# Outputting a histogram representation of a set of marks

inMarks = input("Enter a space-separated list of marks:\n")
marks = [int(mark) for mark in inMarks.split(' ')]

fails = 0
thirds = 0
lowerSeconds = 0
upperSeconds = 0
firsts = 0

for mark in marks:
    if mark < 50:
        fails += 1
    elif mark in range(50, 60):
        thirds += 1
    elif mark in range(60, 70):
        lowerSeconds += 1
    elif mark in range(70, 75):
        upperSeconds += 1
    else:
        firsts += 1

print(f"1 |{'X' * firsts}")
print(f"2+|{'X' * upperSeconds}")
print(f"2-|{'X' * lowerSeconds}")
print(f"3 |{'X' * thirds}")
print(f"F |{'X' * fails}")
