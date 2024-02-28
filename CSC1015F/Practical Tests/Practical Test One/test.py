# Adam Foflonker
# FFLADA001
# Calculating lift

airDensity = eval(input("Enter the value of the air density, rho:\n"))
velocity = eval(input("Enter the value of the velocity or true airspeed, v:\n"))
liftCoeff = eval(input("Enter the value of the lift coefficient, R_e:\n"))
area = eval(input("Enter the value of the Reference Area, A:\n"))

lift = 0.5 * airDensity * (velocity ** 2) * area * (24 / liftCoeff)
print(f"The lift force, F_L, is {round(lift)}.")