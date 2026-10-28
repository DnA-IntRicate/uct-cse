# Adam Foflonker
# FFLADA001
# 19/03/24

availCapacity = 50
print(f"The available capacity is {availCapacity}.")

while availCapacity != 0:
    nextItem = eval(input("Enter the mass of the next item:\n"))

    if nextItem > availCapacity:
        print("That's too big.")
    else:
        availCapacity -= nextItem

    print(f"Remaining capacity: {availCapacity}.")
