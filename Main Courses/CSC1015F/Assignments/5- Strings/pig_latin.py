# Adam Foflonker
# FFLADA001
# 14/03/24
# Pig Latin

sentence = input("Enter a sentence:\n")

i = 0
output = ""
while i < len(sentence):
    nextSpace = sentence.find(" ", i)
    word = sentence[i:] if nextSpace == -1 else sentence[i:nextSpace]

    if word[0].lower() in "aeiou":
        word += "way"
    else:
        consonants = ""
        for c in word:
            if c.lower() in "aeiou":
                break

            consonants += c

        word = (word[len(consonants):] + "a" + consonants + "ay").lower()

    output += word + " "

    if nextSpace == -1:
        break

    i = nextSpace + 1

print(output)
