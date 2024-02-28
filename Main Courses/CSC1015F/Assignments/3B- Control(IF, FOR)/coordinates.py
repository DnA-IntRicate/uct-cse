# Adam Foflonker
# FFLADA001
# Checking if a set of numbers are geographical coordinates

# Form: degrees/minutes/seconds

latDeg = eval(input("Enter first number:\n"))
latMin = eval(input("Enter second number:\n"))
latSec = eval(input("Enter third number:\n"))
longDeg = eval(input("Enter fourth number:\n"))
longMin = eval(input("Enter fifth number:\n"))
longSec = eval(input("Enter sixth number:\n"))

valid = (latDeg in range(-90, 91)) and (longDeg in range(-180, 181)) and (latMin in range(0, 60)) and (longMin in range(0, 60)) and (latSec in range(0, 60)) and (longSec in range(0, 60))
if valid:
    print("WOW! Looks like geographic coordinates!")
else:
    print("Hmmm ... looks like 6 random numbers.")
