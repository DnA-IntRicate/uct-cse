length = eval(input("Enter the length:\n"))
width = eval(input("Enter the width:\n"))
height = eval(input("Enter the height:\n"))

if (length <= 0) or (width <= 0) or (height <= 0):
    print("Dimensions must be greater than zero.")
    exit()

vol = length * width * height
print("The volume is %.2f." % vol)

cost = 0.0
if (vol >= 0) and (vol < 18):
    cost = 14.65
elif (vol >= 18) and (vol < 140):
    cost = 5.95
elif (vol >= 140) and (vol < 440):
    cost = 12.00
elif (vol >= 440) and (vol < 2648):
    cost = 14.65
else:
    print("Shipping cost is not available.\nPackage too large.")
    exit()
    
print("Shipping cost is %.2f." % cost)
