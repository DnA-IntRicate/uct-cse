# testromanutil.py
# 8 tests

# >>> from_roman('IX')  # 10 - 1
#9

# >>> from_roman('XL')  # 50 - 10
# 40

"""
Doctests for the from_roman function in romanutil.py

>>> from romanutil import from_roman

>>> from_roman('III')
3

>>> from_roman('IV')  # Subtractive case: 5 - 1
4

>>> from_roman('LVIII')  # 50 + 5 + 1 + 1 + 1
58

>>> from_roman('MCMXCIV')  # 1000 + 900 + 90 + 4
1994



>>> from_roman('CDXLIV')  # 400 + 40 + 4
444

>>> from_roman('MMMCMXCIX')  # Largest number representable (3999)
3999

"""
import doctest
doctest.testmod(verbose=True)