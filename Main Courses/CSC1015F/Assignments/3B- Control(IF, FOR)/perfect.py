# Adam Foflonker
# FFLADA001
# Finding perfect numbers

number = eval(input("Enter a number:\n"))

divisorsStr = ""
sum = 0
for i in range(1, number):
    if number % i == 0:
        divisorsStr += str(i) + " "
        sum += i

print(f"The proper divisors of {number} are:")
print(divisorsStr, end="\n\n")

if sum == number:
    print(f"{number} is a perfect number.")
else:
    print(f"{number} is not a perfect number.")
