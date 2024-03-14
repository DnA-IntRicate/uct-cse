# Adam Foflonker
# FFLADA001
# 14/03/24
# String splitting

sentence = input("Enter a sentence:\n")

output = sentence[0].lower()
i = 1
while i < len(sentence):
    if sentence[i] == " ":
        output += ", " + sentence[i + 1].lower()
        i += 2
        continue

    output += sentence[i].lower()
    i += 1

print("The word list: {0}.".format(output))
