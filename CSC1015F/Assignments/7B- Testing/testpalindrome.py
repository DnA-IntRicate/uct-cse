# Adam Foflonker
# FFLADA001
# 03/04/24
# Testing palindrome.py

### Test Cases ###
# 1. empty:         ""
# 2. len == 1:      "a"
# 3. end of loop:   "racecar"
# 4. break loop:    "Curry"
# 5. len == 3:      "ada"

"""
>>> from palindrome import is_palindrome
>>> is_palindrome("")
True
>>> is_palindrome("a")
True
>>> is_palindrome("racecar")
True
>>> is_palindrome("Curry")
False
>>> is_palindrome("ada")
True

"""

import doctest
doctest.testmod(verbose=True)
