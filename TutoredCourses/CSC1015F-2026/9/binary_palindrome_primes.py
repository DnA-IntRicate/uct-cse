# Adam Foflonker
# 15/05/26
# Assignment 9 Question 1 sample solution

import sys


def is_palindrome(s: str) -> bool:
    if not s:
        return True

    if len(s) == 1:
        return True

    if s[0] != s[-1]:
        return False

    return is_palindrome(s[1:-1])


def is_prime(num: int, divisor: int = 2) -> bool:
    if num < 2:
        return False

    if divisor * divisor > num:
        return True

    if num % divisor == 0:
        return False

    return is_prime(num, divisor + 1)


def to_binary(num: int) -> str:
    return f"{num:b}"


def binary_palindrome_primes(m: int, n: int) -> list[int]:
    if m >= n:
        return []

    if not is_prime(m):
        return binary_palindrome_primes(m + 1, n)

    return [m] + binary_palindrome_primes(m + 1, n) if is_palindrome(to_binary(m)) else binary_palindrome_primes(m + 1, n)


def main():
    m = int(input("Enter the starting point M:\n"))
    n = int(input("Enter the ending point N:\n"))

    print(f"Binary palindrome primes between {m} and {n} are:\n" +
        "\n".join(f"{num} (binary: {to_binary(num)})"
                  for num in binary_palindrome_primes(m, n))
    )


if __name__ == "__main__":
    sys.setrecursionlimit(30000)
    main()
