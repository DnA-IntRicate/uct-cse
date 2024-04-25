# Adam Foflonker
# FFLADA001
# 17/04/24
# Recursively finding palindromic primes between two integers

from palindrome import IsPalindrome
import sys

# i is used to store the recursion index of the function; it is not intended to be modified by the caller!
def IsPrime(a: int, i: int = 2) -> bool:
    if a <= 1:
        return False

    if a == 2:
        return True

    if a % 2 == 0:
        return False

    if (i ** 2) > a:
        return True

    if a % i == 0:
        return False

    return IsPrime(a, i + 1)

def PrintPalindromicPrimesInRange(n: int, m: int):  # I don't like snake_case lol
    if IsPrime(n) and IsPalindrome(str(n)):
        print(n)

    if n == m:  # Check for the base-case down here to ensure that the final value is printed if it is a palindromic prime
        return

    PrintPalindromicPrimesInRange(n + 1, m)


if __name__ == "__main__":
    sys.setrecursionlimit(30000)

    n = eval(input("Enter the starting point N:\n"))
    m = eval(input("Enter the ending point M:\n"))

    print("The palindromic primes are:")
    PrintPalindromicPrimesInRange(n, m)
