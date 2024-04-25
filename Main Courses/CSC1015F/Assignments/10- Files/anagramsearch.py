# Adam Foflonker
# FFLADA001
# 25/04/24
# Searching a file for anagrams of a given word and printing the results in alphabetical order

import os

FILEPATH: str = "EnglishWords.txt"

# Returns true if a and b contain the same characters as each other. Does not care about their lengths
def StringCompare(a: str, b: str) -> bool:
    for c in a:
        if c not in b:
            return False

    for c in b:
        if c not in a:
            return False

    return True

# Returns a dict/map where each char in s is mapped to the amount of times it occurs in s
def GetStringCharCountMap(s: str) -> dict[str, int]:
    res: dict[str, int] = {}
    for c in s:
        if c not in res.keys():
            res[c] = 1
        else:
            res[c] += 1

    return res

# Returns true if a and b are anagrams of each other
def IsAnagram(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False

    myA, myB = a.lower(), b.lower()

    if myA == myB:  # Equal words are not anagrams of each other
        return False

    if not StringCompare(myA, myB):
        return False

    # The keys in these 2 maps should always be equal
    aCountMap, bCountMap = GetStringCharCountMap(myA), GetStringCharCountMap(myB)
    for c in myA:
        if aCountMap[c] != bCountMap[c]:
            return False

    return True

# Bubble sorts the list into alphabetical order in-place
def SortAlphabetical(lst: list[str]):
    for i in range(len(lst)):
        for j in range(len(lst) - 1):
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]

# Opens 'EnglishWords.txt' and returns a list containing all words from START to the end of file
def OpenWordList(filePath: str = FILEPATH) -> list[str]:
    file = open(filePath, 'r')
    lines = [line.strip() for line in file.readlines() if (line != '') and (line != '\n')]
    lines = lines[lines.index("START") + 1:]
    file.close()

    return lines

# Returns a list containing all the anagrams of word in 'EnglishWords.txt' in alphabetical order
# This function is intended to be private
def _FindAnagramsOf(word: str) -> list[str]:
    wordList = OpenWordList()

    res = []
    for line in wordList:
        if IsAnagram(word, line):
            res.append(line)

    SortAlphabetical(res)

    return res

if __name__ == "__main__":
    print("***** Anagram Finder *****")

    if not os.path.exists(FILEPATH):
        print(f"Sorry, could not find file '{FILEPATH}'.")
        exit()

    word = input("Enter a word:\n")

    anagrams = _FindAnagramsOf(word)
    if not anagrams:
        print(f"Sorry, anagrams of '{word}' could not be found.")
        exit()

    print(anagrams)
