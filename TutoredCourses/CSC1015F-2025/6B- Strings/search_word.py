# Assignment 6
# search_word.py sample solution
# Adam Foflonker (FFLADA001)
# 02/04/25

sentence = input("Enter a sentence:\n").lower()
query = input("Enter the word to find:\n").lower()

# We cannot use str.split() function
foundQuery = False
matchCount = 0
idxFirst = -1

for i, c in enumerate(sentence):
    if matchCount == len(query) - 1:
        foundQuery = True
        break

    if c == query[matchCount]:
        matchCount += 1

        if idxFirst == -1:
            idxFirst = i
    else:
        matchCount = 0
        idxFirst = -1

if foundQuery:
    print(f"The word '{query}' is in the sentence.")
    print(f"It first appears at index {idxFirst}.")
else:
    print(f"The word '{query}' is NOT in the sentence.")

# Test case:
# The Quick Brown Fox Jumped Over The Lazy Dog
# brown
