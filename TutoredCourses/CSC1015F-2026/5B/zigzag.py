# Adam Foflonker
# Assignment 5B sample solution
# 01/04/2026


numbers = sorted(list(map(int, input("Enter numbers a sequence of space-separated numbers:\n").strip().split())))
zigzag = [x for pair in zip(numbers, reversed(numbers)) for x in pair][:len(numbers)]
print(zigzag)
