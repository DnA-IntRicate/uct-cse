# Adam Foflonker
# FFLADA001
# 25/04/24
# Searching a file for sets of anagrams and printing them in alphabetical order

import anagramsearch as ag

# Returns a list of all the words in wordList of the specified length
def FindAllWordsOfLength(length: int, wordList: list[str]) -> list[str]:
    res = []
    for word in wordList:
        if len(word) == length:
            res.append(word)

    return res

# Returns a list of all the anagrams of word in wordList
def FindAnagramsInList(word: str, wordList: list[str]) -> list[str]:
    res = []
    for w in wordList:
        if ag.IsAnagram(word, w):
            res.append(w)

    return res

# Returns a list of lists of strings containing each anagram set of the specified length in wordList sorted alphabetically
def FindAnagramSets(length: int, wordList: list[str]) -> list[list[str]]:
    wordsOfLength = FindAllWordsOfLength(length, wordList)

    res: list[list[str]] = []
    usedWords = []

    for word in wordsOfLength:
        if word not in usedWords:
            anagramList = [word] + FindAnagramsInList(word, wordsOfLength)
            if len(anagramList) > 1:
                res.append(anagramList)

            usedWords += anagramList

    for lst in res:
        ag.SortAlphabetical(lst)

    return sorted(res, key=lambda x: x[0]) # Sort on x[0] (first string in each list) in alphabetical order

def WriteAnagramSetsToFile(filePath: str, anagramSets: list[list[str]]):
    file = open(filePath, 'w')

    for set in anagramSets:
        file.write(str(set) + '\n')

    file.flush()
    file.close()

if __name__ == "__main__":
    print("***** Anagram Set Search *****")
    wordLength = eval(input("Enter word length:\n"))

    print("Searching...")
    wordList = ag.OpenWordList()
    anagramSets = FindAnagramSets(wordLength, wordList)

    filePath = input("Enter file name:\n")
    print("Writing results...")
    WriteAnagramSetsToFile(filePath, anagramSets)
