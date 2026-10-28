# dateutil.py
# Lebeko Poulo
# 15/04/2025

def format_date(day, month, year):
    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    if month not in months or day < 1:
        return "Invalid date"

    if month in {1, 3, 5, 7, 8, 10, 12}:
        max_day = 31
    elif month in {4, 6, 9, 11}:
        max_day = 30
    elif month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_day = 29
        else:
            max_day = 28

    if day > max_day:
        return "Invalid date"

    return f"{day} {months[month]} {year}"
