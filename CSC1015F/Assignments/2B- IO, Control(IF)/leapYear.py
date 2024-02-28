# A program to determine whether a year is a leap year or not.
# Author: Adam Foflonker (FFLADA001)
# Date (dd/mm/yyyy): 22/02/2024

def IsLeapYear(year: int) -> bool:
    if year % 400 == 0:
        return True

    if (year % 4 == 0) and (year % 100 != 0):
        return True

    return False

year = eval(input("Enter a year:\n"))
strModifier = " " if IsLeapYear(year) else " not "
print(f"{year} is{strModifier}a leap year.")
