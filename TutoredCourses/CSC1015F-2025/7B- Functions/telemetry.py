# Assignment 7
# telemetry.py sample solution
# Adam Foflonker (FFLADA001)
# 27/03/24

# "... START speed:3200|90.5 lat=51.5074 long=-0.1278 name=Alex Turner END ..."

# Declare global constants for use in multiple methods.
TOKEN_BEGIN = "BEGIN"
TOKEN_END = "END"

def get_data_block(raw_string: str) -> str:
    """
    Extracts the telemetry block between START and END markers.
    """

    start = raw_string.find("START")
    end = raw_string.find("END")


def rpm(data_block: str):
    """
    Extracts and returns the engine RPM as an integer.
    """
    # Your code here


def speed(data_block: str):
    """
    Extracts and returns the vehicle speed as a float.
    """
    # Your code here

def coordinates(data_block: str):
    """
    Extracts and returns latitude and longitude from the telemetry block as a tuple.
    """
    # Your code here

def driver_name(data_block: str):
    """
    Extracts and returns the driver's name in title case.
    """
    # Your code here

def main():
    pass
    # Vehicle Telemetry
    # Your code here

# DO NOT modify
if __name__ == "__main__":
    main()
