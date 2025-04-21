"""
Doctests for the format_date function in dateutil.py

>>> from traceable_dateutil import format_date

# 1. Invalid month
>>> format_date(21, 13, 2024)
'Invalid date'

# 2. Invalid day (<1)
>>> format_date(0, 3, 2024)
'Invalid date'

# 3. Valid 31-day month
>>> format_date(15, 5, 2024)
'15 May 2024'

# 4. 31-day month, invalid day (>31)
>>> format_date(32, 7, 2024)
'Invalid date'

# 5. Valid 30-day month
>>> format_date(30, 4, 2024)
'30 April 2024'

# 6. 30-day month, invalid day
>>> format_date(31, 9, 2024)
'Invalid date'

# 7. February in leap year, valid day
>>> format_date(29, 2, 2024)
'29 February 2024'

# 8. February in non-leap year, valid day
>>> format_date(28, 2, 2023)
'28 February 2023'

# 9. February in non-leap year, invalid day
>>> format_date(29, 2, 2023)
'Invalid date'

"""
import doctest
doctest.testmod(verbose=True)
