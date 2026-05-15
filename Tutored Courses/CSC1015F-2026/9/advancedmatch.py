# Adam Foflonker
# FFLADA001
# 17/04/24
# Advanced recursive pattern matching

# '?' - Represents a single character ('_' in SQL)
# '*' - Represents zero or more characters ('%' in SQL)
def match(pattern: str, word: str) -> bool:
    if not pattern and not word:
        return True

    if not pattern or not word:
        return False

    if not word and pattern == '*':
        return True

    if ('*' not in pattern) and (len(pattern) != len(word)):
        return False

    if pattern[0] in ['?', word[0]]:
        return match(pattern[1:], word[1:])

    if pattern[0] == '*':
        return MatchAny(pattern[1:], word)

    return False

# Handles matching the pattern if a star char is encountered
def MatchAny(pattern: str, word: str) -> bool:
    if not pattern:
        return True

    if not word:
        return False

    return match(pattern, word) or MatchAny(pattern, word[1:])
