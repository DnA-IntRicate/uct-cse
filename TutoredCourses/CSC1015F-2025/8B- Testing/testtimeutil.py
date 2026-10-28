# testtimeutil.py
"""
>>> import timeutil
>>> timeutil.validate(':00 a.m.')
False
>>> timeutil.validate('h0:00 a.m.')
False
>>> timeutil.validate('1:00 fm')
False
>>> timeutil.validate('01:00 a.m.')
False
>>> timeutil.validate('12: 1 a.m.')
False
>>> timeutil.validate('55:66 p.m.')
False

"""
import doctest
doctest.testmod(verbose=True)
