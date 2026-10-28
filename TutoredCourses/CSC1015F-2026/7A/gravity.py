# 7A- W4AB Sample solution
# Adam Foflonker
# 15/04/26


def distance(duration: float) -> float:
    return (9.8 * (duration ** 2)) / 2


def main():
    duration = float(input("Enter the travel time:\n"))
    if (duration < 0.0):
        print("The travel time must be zero or more.")
        return

    print(f"The distance covered is {distance(duration):.2f}.")


if __name__ == '__main__':
    main()
