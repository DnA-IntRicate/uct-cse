# FFLADA001
# Adam Foflonker
# 16/04/24
# Right-justifying a list of strings


# Returns the length of the longest string in the list
def LengthLongestString(strings: list[str]) -> int:
    longestLength = len(strings[0])

    for i in range(len(strings)):
        if len(strings[i]) > longestLength:
            longestLength = len(strings[i])

    return longestLength

def right_justify(strings: list[str]) -> list[str]:
    """
    The function accepts a list of digit strings of various lengths as a parameter,
    finds the length, l, of the longest, and returns a new list where each digit string is
    a copy of the original right-justified to a width of l.
    """
    if not strings:
        return []

    longestLength = LengthLongestString(strings)
    res = []

    for s in strings:
        if len(s) != longestLength:
            res.append(('0' * (longestLength - len(s))) + s)
            continue

        res.append(s)

    return res

# testformat.py
"""
>>> import format
>>> format.right_justify([])
[]
>>> format.right_justify(['1'])
['1']
>>> format.right_justify(['092346'])
['092346']
>>> format.right_justify(['1', '10'])
['01', '10']
>>> format.right_justify(['29', '3'])
['29', '03']
>>> format.right_justify(['002368', '9862', '100'])
['002368', '009862', '000100']
>>> a = ['32', '2236']
>>> format.right_justify(a)
['0032', '2236']
>>> a[0] == '32'
True

"""

if __name__ == '__main__':
    import doctest
    doctest.testfile('format.py', verbose=True)
