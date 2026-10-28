# Assignment 3B
# perfect.py Sample Solution
# Adam Foflonker
# 09/03/25

number = int(input("Enter a number:\n"))

# A perfect number is a positive integer that is equal to the sum of its proper divisors.
# 6 is a perfect number because its proper divisors are 1, 2 & 3; 1 + 2 + 3 = 6

print(f"The proper divisors of {number} are:")

sumDivisors = 0
outStr = ""

for i in range(1, number):
    if number % i == 0:
        outStr += str(i) + " "
        sumDivisors += i

print(outStr.strip()) # Remove the leading whitespace left from the array
print() # Automark wants an extra newline

if (sumDivisors == number):
    print(f"{number} is a perfect number.")
else:
    print(f"{number} is not a perfect number.")
