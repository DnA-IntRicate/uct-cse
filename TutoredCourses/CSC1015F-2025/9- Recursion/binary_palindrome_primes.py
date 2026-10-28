
def is_prime(n, divisor=2):
    if n <= 0:
        return False

    if (n == 1) or (n == 2):
        return True

    if n % divisor == 0:
        return False

    return is_prime(n - 1, divisor + 1)


def to_binary(n):
    # Recursive integer to binary string
    pass


def is_palindrome(s):
    if len(s) <= 1:
        return True

    if s[1] != s[-1]:
        return False

    return is_palindrome(s[1:-1])


def search_palindromic_primes(n, m):
    pass
    # Recursive range traversal

def main():
    pass
    # your code here

# Main block to take input and start the recursive search
if __name__ == "__main__":
    main()

