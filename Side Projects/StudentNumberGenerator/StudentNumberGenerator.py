##################################################################################
# MIT License
#
# Copyright (c) 2024 Adam Foflonker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
##################################################################################

####################################################################################################
# This program aims to generate a student number based off of a student's name and surname
#   - A student number constitutes of 9 characters;
#   - 3 characters from the first 3 consonants of a person’s surname
#   - 3 characters from the first 3 letters of the person’s first name
#   - 3 numerals being the number that represents what number you are in the list of people who
#   - have the same 6 characters. For example MCHJOR023
#
# a)
#   Write a program to enter an unspecified number of names of students and construct a valid
#   student number.
#   You can use an array to store the first 6 characters and search through that array to check if
#   there exists a same combination of the first 6 characters. This will allow you to construct
#   the last 3 digits.
#
# b)
#   After some inputs it so happened that there were students whose names had less than 3
#   consonants or less than 3 characters.
#   Edit the first code so that:
#   If the first or last name has less that 3 consonants use the first 3 letters, if it has less than 3
#   letters append a cipher of the first letter(s) at the end ( for example Xi -> XIQ, JO->JOC)
#   The cipher is the letter 7 positions behind in the alphabet.
#   Should the cipher go past A, it cycles back to Z and backwards.
#
# Scenario created by
# Carlos Muravu
# 19 April 2024
#
# Program written by
# Adam Foflonker
# 20 April 2024
####################################################################################################


# Will be used to store the amount of times the alpha part of each student number occured.
g_StudentNumberAlphaMap: dict[str, int] = {}

def IsVowel(c: str) -> bool:
    if c in "aeiou":
        return True

    return False

def IsConsonant(c: str) -> bool:
    return not IsVowel(c)

def ReadLinesFromFile(filePath: str) -> list[str]:
    file = open(filePath, 'r')
    res = [line.strip() for line in file.readlines()]
    file.close()

    return res

def RightJustifyIntAsStr(i: int, size: int = 3) -> str:
    if len(str(i)) == size:
        return str(i)

    return ('0' * (size - len(str(i)))) + str(i)

def ApplyCipher(s: str) -> str:
    if len(s) >= 3:
        return s

    if len(s) == 1: # Handles if the name/surname is 1 character.
        return s + (chr(((ord(s[0]) - ord('A') + 7) % 26) + ord('A'))) * 2

    return s + chr(((ord(s[0]) - ord('A') + 7) % 26) + ord('A'))

def GenerateStudentNumber(name: str) -> str:
    foreNames = name[:name.rfind(' ')]      # We want to find the last space
    surname = name[name.rfind(' ') + 1:]

    consonants = ""
    if len(surname) > 3:
        for c in surname:
            if IsConsonant(c):
                consonants += c

            if len(consonants) == 3:
                break
    else:
        consonants = ApplyCipher(surname)

    foreNameChars = ""
    if len(foreNames) < 3:
        foreNameChars = ApplyCipher(foreNames)
    else:
        foreNameChars = foreNames[:3]

    studentNumberAlphas = (consonants + foreNameChars).upper()

    if studentNumberAlphas not in g_StudentNumberAlphaMap.keys():
        g_StudentNumberAlphaMap[studentNumberAlphas] = 1
    else:
        g_StudentNumberAlphaMap[studentNumberAlphas] += 1

    return studentNumberAlphas + RightJustifyIntAsStr(g_StudentNumberAlphaMap[studentNumberAlphas])

if __name__ == "__main__":
    filePath = input("Enter the path to your names file:\n")
    names = ReadLinesFromFile(filePath)

    for name in names:
        print(f"{GenerateStudentNumber(name)}:\t{name}")

    print("DONE!\n")
    input("Press Enter to continue...")
