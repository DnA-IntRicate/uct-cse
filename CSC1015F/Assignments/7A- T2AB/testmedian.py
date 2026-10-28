# FFLADA001
# Adam Foflonker
# 09/04/24
# Testing median.py

### Test Cases ###
# 1. (min > mid) and ((mid > max) and (min > mid)): (5, 2, 1)
# 2. (min > mid) and (mid > max):                   (5, 2, 3)
# 3. (min > mid):                                   (5, 2, 10)
# 4. (mid > max) and (min > mid):                   (11, 12, 10)
# 5. (mid > max):                                   (2, 9, 6)
# 6. return mid:                                    (2, 4, 8)

'''
>>> from median import median_value
>>> median_value(5, 2, 1)
2
>>> median_value(5, 2, 3)
3
>>> median_value(5, 2, 10)
5
>>> median_value(11, 12, 10)
11
>>> median_value(2, 9, 6)
6
>>> median_value(2, 4, 8)
4

'''

import doctest
doctest.testmod(verbose=True)
