# Adam Foflonker
# FFLADA001
# 14/03/24
# DateTime format conversions

inDateTime = input("Enter the date and time (yyyy-mm-dd hh:mm):\n")

year = inDateTime[:4]
month = inDateTime[5:7]
day = str(int(inDateTime[8:10])) # Quick & dirty way to get rid of leading 0s
time = inDateTime[11:]
hour = time[:2]
min = time[3:]

meridiem = "pm" if int(hour) >= 12 else "am"

if hour == "00":
    hour = "12"
elif int(hour) > 12:
    hour = str(int(hour) % 12)
else:
    hour = str(int(hour))

output = f"{hour}:{min} {meridiem} on the {day}"

if (day[0] == "1") and (len(day) > 1):
    output += "th"
else:
    lastDigitOfDay = day[len(day) - 1]
    if lastDigitOfDay == "1":
        output += "st"
    elif lastDigitOfDay == "2":
        output += "nd"
    elif lastDigitOfDay == "3":
        output += "rd"
    else:
        output += "th"

monthStr = "January"
if month == "02":
    monthStr = "February"
elif month == "03":
    monthStr = "March"
elif month == "04":
    monthStr = "April"
elif month == "05":
    monthStr = "May"
elif month == "06":
    monthStr = "June"
elif month == "07":
    monthStr = "July"
elif month == "08":
    monthStr = "August"
elif month == "09":
    monthStr = "September"
elif month == "10":
    monthStr = "October"
elif month == "11":
    monthStr = "November"
elif month == "12":
    monthStr = "December"

output += " of {0} '{1}".format(monthStr, year[len(year) - 2:])
print(output)
