# A program checking the validity of a time entered by the user as a set of three integers.
# Author: Adam Foflonker (FFLADA001)
# Date (dd/mm/yyyy): 22/02/2024

numHours = eval(input("Enter the hours:\n"))
numMinutes = eval(input("Enter the minutes:\n"))
numSeconds = eval(input("Enter the seconds:\n"))

valid = (numHours in range(0, 24)) and (numMinutes in range(0, 60)) and (numSeconds in range(0, 60))
if valid:
    print("Your time is valid.")
else:
    print("Your time is invalid.")
