# Adam Foflonker
# FFLADA001
# 06/03/24
# Printing a sequence of numbers

number = eval(input("Enter a number between -6 and 93:\n"))

if not number in range(-6, 94):
    print("Invalid input! The value of 'n' should be between -6 and 93.")
    exit()

output = ""
for i in range(number, number + 7):
    if i in range(0, 10):
        output += " " + str(i) + " "
    else:
        output += str(i) + " "

output.strip()
print(output)
