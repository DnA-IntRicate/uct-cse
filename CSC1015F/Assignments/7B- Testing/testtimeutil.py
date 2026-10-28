# Adam Foflonker
# FFLADA001
# 04/04/24
# Testing timeutil.py

### Test Cases ###
# 1. colon<1:                                               ":20 p.m."
# 2. len(hours)>2 or len(hours)<1 or not hours.isdigit():   "aa:20 p.m."
# 3. len(hours)==2 and int(hours[0])==0:                    "01:20 p.m."
# 4. not suffix==' a.m.' and not suffix==' p.m.':           "11:01 foo."
# 5. not len(minutes)==2 or not minutes.isdigit():          "11:aa p.m."
# 6. hours>0 and hours<13 and minutes>-1 and minutes<60:    "12:59 p.m."

"""
>>> from timeutil import validate
>>> validate(":20 p.m.")
False
>>> validate("aa:20 p.m.")
False
>>> validate("01:20 p.m.")
False
>>> validate("11:01 foo.")
False
>>> validate("11:aa p.m.")
False
>>> validate("12:59 p.m.")
True

"""

import doctest
doctest.testmod(verbose=True)
