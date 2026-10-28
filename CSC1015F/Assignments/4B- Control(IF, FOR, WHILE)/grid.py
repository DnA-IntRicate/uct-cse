# Adam Foflonker
# FFLADA001
# 06/03/24
# Printing a grid of numbers

number = eval(input("Enter a number between -6 and 2:\n"))

if not number in range(-6, 3):
    print("Invalid input! The value of 'n' should be between -6 and 2.")
    exit()

for i in range(number, number + 41, 7):
    output = ""
    for j in range(i, i + 7):
        output += (" " if j in range(0, 10) else "") + str(j) + " "

    output.strip()
    print(output)
