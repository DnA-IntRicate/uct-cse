# Assignment 7
# syllables.py sample solution
# Adam Foflonker (FFLADA001)
# 27/03/24

def is_vowel(letter: str) -> bool:
    return letter.lower() in "aeiouy"

def next_vowel(word: str, index: int) -> int:
    for i in range(index + 1, len(word)):
        if is_vowel(word[i]):
            return i

    return len(word)

def count_syllables(word: str) -> int:
    count = 0

    if is_vowel(word[0]):
        count += 1

    for i in range(1, len(word)):
        if is_vowel(word[i]) and not is_vowel(word[i - 1]): # Counting vowel-sounds and groupings.
            count += 1

    if (word[len(word) - 1] == "e") and (not is_vowel(word[len(word) - 2])):
        count -= 1

    return max(count, 1)    # Ensure syllable count is not 0 or negative

def main():
    word = input("Enter a word (or \'q\' to quit):\n")
    while word != "q":
        syllableCount = count_syllables(word)
        pluralSyllableStr = "syllable" if syllableCount == 1 else "syllables"

        print(f"The word '{word}' has {syllableCount} {pluralSyllableStr}.", end="\n\n")
        word = input("Enter a word (or \'q\' to quit):\n")

if __name__ == "__main__":
    main()
