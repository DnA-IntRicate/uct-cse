# Test case 1*: Check if an empty string is a palindrome - AB
# Test case 2*: Check if a single character string is a palindrome - ACD
# Test case 3*: Check if a two character string is a palindrome - ACEFH
# Test case 4: Check if a two character string is not a palindrome - ACEFG
# Test case 5: Check if a three character string is a palindrome - ACEFH
# Test case 6*: Check if a three character string is not a palindrome - ACEFG
# Test case 7: Check if a longer palindrome is correctly identified - ACEFH
# Test case 8: Check if a longer non-palindrome is correctly identified - ACEFG
# Test case 9: Check if case sensitivity is taken into account - ACEFG
# Test case 10*: Check if white space is ignored - ACEFGH
"""
>>> import palindrome

Test case 1: Check if an empty string is a palindrome - AB
>>> palindrome.is_palindrome("")
True

Test case 2: Check if a single character string is a palindrome - ACD
>>> palindrome.is_palindrome("a")
True

Test case 3: Check if a two character string is a palindrome - ACEFH
>>> palindrome.is_palindrome("aa")
True

Test case 6: Check if a three character string is not a palindrome - ACEFG
>>> palindrome.is_palindrome("abc")
False

Test case 10: Check if white space is ignored - ACEFGH
>>> palindrome.is_palindrome("A Santa at NASA")
False


"""
import doctest
doctest.testmod(verbose=True)
