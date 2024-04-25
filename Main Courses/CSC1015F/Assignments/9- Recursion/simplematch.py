# Adam Foflonker
# FFLADA001
# 17/04/24
# Simple recursive pattern matching

# '?' - Represents a single character ('_' in SQL)
def match(pattern: str, word: str) -> bool:
    if not pattern and not word:
        return True

    if len(pattern) != len(word):
        return False

    if pattern[0] in ['?', word[0]]:
        return match(pattern[1:], word[1:])

    return False
