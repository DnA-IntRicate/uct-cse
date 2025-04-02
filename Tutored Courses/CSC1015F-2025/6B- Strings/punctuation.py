# Assignment 6
# punctuation.py sample solution
# Adam Foflonker (FFLADA001)
# 02/04/25

par = input("Enter a paragraph of any length:\n")

parNoPunc = ""
wordBuf = ""
uniqueWords: list[str] = []

for c in par:
    if (c == " ") or (c == "'") or (c == "-") or (ord(c.lower()) in range(ord("a"), ord("z") + 1)):
        parNoPunc += c

for c in parNoPunc:
    if c != " ":
        wordBuf += c
        continue

    if wordBuf not in uniqueWords:
        uniqueWords.append(wordBuf)

    wordBuf = ""

# Handle the final word which does not end on a space
if wordBuf not in uniqueWords:
    uniqueWords.append(wordBuf)

print(f"A paragraph without punctuation:\n{parNoPunc}")
print(f"The number of unique words in a paragraph:\n{len(uniqueWords)}")
print(f"The unique words are:\n{uniqueWords}")

# Test case:
# Wait... did you see that!? It was incredible; I couldn't believe my eyes: a flying cat!
