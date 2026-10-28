from math import pi

def surface_area(diameter: float, height: float) -> float:
    return 2 * pi * ((diameter / 2) ** 2) + (pi * diameter * height)

def main():
    height = float(input("Enter the height of the cylinder:\n"))
    diameter = float(input("Enter the diameter of the base:\n"))

    if (height <= 0) or (diameter <= 0):
        print("The height and diameter must be greater than zero.")
        exit()

    surfaceArea = surface_area(diameter, height)
    print("The surface area is {:.2f}.".format(surfaceArea))


if __name__ == "__main__":
    main()
