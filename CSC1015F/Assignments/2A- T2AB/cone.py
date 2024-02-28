# Adam Foflonker
# FFLADA001
# Calculating the volume of a cone.
import math


height = float(input("Enter the height of the cone:\n"))
radius = float(input("Enter the radius of the base:\n"))

if (height <= 0.0) or (radius <= 0.0):
    print("The height and radius must be greater than zero.")
    exit()

volume = (height / 3) * math.pi * (radius**2)
print("The volume is %.2f." % volume)
