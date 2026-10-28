# Adam Foflonker
# FFLADA001
# 27/03/24
# Extracting useful information from raw data.

# Declare global constants for use in multiple methods.
TOKEN_BEGIN = "BEGIN"
TOKEN_END = "END"

def location(block: str) -> str:    # Prefer explicit return-type and parameter declaration over implicit.
    locationBlock = block[block.find("S ") + 2:block.find(TOKEN_END)]

    return locationBlock[::-1].title().strip()

def temperature(block: str) -> float:
    startIdx = block.find(TOKEN_BEGIN) + len(TOKEN_BEGIN)
    endIdx = block.find("_")

    return float(block[startIdx:endIdx])

def x_coordinate(block: str) -> str:
    return block[block.find(":") + 1:block.find(",")]

def y_coordinate(block: str) -> str:
    firstComma = block.find(",")
    return block[firstComma + 1:block.find(" ", firstComma)]

def pressure(block: str) -> float:
    return float(block[block.find("_") + 1:block.find(":")])

def get_block(data: str) -> str:
    startIdx = data.find(TOKEN_BEGIN)
    endIdx = data.find(TOKEN_END) + len(TOKEN_END)

    return data[startIdx:endIdx]

def main():
    data = input("Enter the raw data:\n")
    block = get_block(data)
    print("Site information:")
    print("Location:", location(block))
    print("Coordinates:", y_coordinate(block), x_coordinate(block))
    print("Temperature: {:.2f} C".format(temperature(block)))
    print("Pressure: {:.2f} hPa".format(pressure(block)))

if __name__=="__main__":
    main()
