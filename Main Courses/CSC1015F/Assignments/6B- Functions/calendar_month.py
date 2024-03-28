# Adam Foflonker
# FFLADA001
# 27/03/24
# Printing a calendar

import math


def day_of_week(day: int, month: int, year: int) -> int:  # Prefer explicit return-type and parameter declaration over implicit.
    m = month
    y = year

    if (m == 1) or (m == 2):
        m += 12
        y -= 1

    h = ((day + math.floor((13 * (m + 1)) / 5) + y + math.floor(y / 4) - math.floor(y / 100) + math.floor(y / 400)) % 7)

    return math.floor(((h + 5) % 7) + 1)

def is_leap(year: int) -> bool:
    if year % 400 == 0:
        return True

    if (year % 4 == 0) and (year % 100 != 0):
        return True

    return False

def month_num(month_name: str) -> int:
    # Using a dictionary/map to quickly pair month-strings to numbers.
    monthIndexMap = {
        "january":    1,
        "february":   2,
        "march":      3,
        "april":      4,
        "may":        5,
        "june":       6,
        "july":       7,
        "august":     8,
        "september":  9,
        "october":    10,
        "november":   11,
        "december":   12
    }

    return monthIndexMap[month_name.lower()]

def num_days_in(month_num: int, year: int) -> int:
    if month_num == 2:
        return 29 if is_leap(year) else 28

    # Using a dictionary/map to pair month-indices to the amount of days they have excluding February
    monthDayMap = {
        1:  31,
        3:  31,
        4:  30,
        5:  31,
        6:  30,
        7:  31,
        8:  31,
        9:  30,
        10: 31,
        11: 30,
        12: 31
    }

    return monthDayMap[month_num]

def num_weeks(month_num: int, year: int) -> int:
    daysInMonth = num_days_in(month_num, year)
    firstDay = day_of_week(1, month_num, year)

    return math.ceil((daysInMonth + firstDay - 1) / 7)

# Utility function to correct padding to the left of numeric strings
def PaddedString(num: int) -> str:
    if num in range(10):
        return " " + str(num)

    return str(num)

def week(week_num: int, start_day: int, days_in_month: int) -> str:
    res = ""
    startOfWeek = 7 * (week_num - 1) + 2 - start_day

    if startOfWeek < 1:
        res += "  "
    else:
        res += PaddedString(startOfWeek)

    for i in range(startOfWeek + 1, startOfWeek + 7):
        res += " "
        if i not in range(1, days_in_month + 1):
            res += "  "
            continue

        res += PaddedString(i)

    return res

def main():
    month = input("Enter month:\n")
    year = eval(input("Enter year:\n"))

    print(month)
    print("Mo Tu We Th Fr Sa Su")

    monthNum = month_num(month)
    for i in range(1, num_weeks(monthNum, year) + 1):
        print(week(i, day_of_week(1, monthNum, year), num_days_in(monthNum, year)))


if __name__=="__main__":
    main()
