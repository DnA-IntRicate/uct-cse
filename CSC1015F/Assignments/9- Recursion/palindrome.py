# Adam Foflonker
# FFLADA001
# 17/04/24
# Recursively determining if a string is a palindrome.

def IsPalindrome(s: str) -> bool:
    if not s:
        return True

    if len(s) == 1:
        return True

    if s[0] != s[-1]:
        return False

    return IsPalindrome(s[1:len(s) - 1])

if __name__ == "__main__":
    inStr = input("Enter a string:\n")

    if IsPalindrome(inStr):
        print("Palindrome!")
    else:
        print("Not a palindrome!")
