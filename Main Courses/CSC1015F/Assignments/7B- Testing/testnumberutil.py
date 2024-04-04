# Adam Foflonker
# FFLADA001
# 03/04/24
# Testing numberutil.py

### Test Cases ###
# 1. (hundreds > 0):                                                            100
# 2. (hundreds > 0) and (remainder > 0) and (remainder < 21):                   113
# 3. (hundreds > 0) and (remainder > 0) and (remainder > 21):                   130
# 4. (hundreds > 0) and (remainder > 0) and (remainder > 21) and (units > 0):   122
# 5. (remainder > 0) and (remainder < 21):                                      13
# 6. (remainder > 0) and (remainder > 21):                                      30
# 7. (remainder > 0) and (remainder > 21) and (units > 0):                      22
# 8. (hundreds == 0) and (remainder == 0):                                      0

"""
>>> from numberutil import aswords
>>> aswords(0)
'zero'
>>> aswords(22)
'twenty two'
>>> aswords(30)
'thirty'
>>> aswords(13)
'thirteen'
>>> aswords(122)
'one hundred and twenty two'
>>> aswords(130)
'one hundred and thirty'
>>> aswords(113)
'one hundred and thirteen'
>>> aswords(100)
'one hundred'

"""

import doctest
doctest.testmod(verbose=True)
