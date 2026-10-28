# Assignment 3B
# amicable.py Sample Solution
# Adam Foflonker
# 09/03/25

numA = int(input("Enter first number:\n"))
numB = int(input("Enter second number:\n"))

# Amicable numbers are 2 positive integers A & B, such that the sum of the proper divisors of A equals B, and vice-versa

sumDivisorsA = 0
for i in range(1, numA):
    if numA % i == 0:
        sumDivisorsA += i

sumDivisorsB = 0
for i in range(1, numB):
    if numB % i == 0:
        sumDivisorsB += i

if (sumDivisorsA == numB) and (sumDivisorsB == numA):
    print(f"{numA} and {numB} are amicable numbers.")
else:
    print(f"{numA} and {numB} are not amicable numbers.")
