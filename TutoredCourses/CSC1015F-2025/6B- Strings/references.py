# Assignment 6
# references.py sample solution
# Adam Foflonker (FFLADA001)
# 14/03/24

reference = input("Enter the reference:\n")

firstParen = reference.find("(")
lastParen = reference.find(")")
titleBeg = lastParen + 2
titleEnd = reference.find(",", titleBeg)
formattedReference = reference[0].capitalize()

i = 1   # Loop control variable
while i < len(reference):   # Iterate over each char in str
    if (i <= firstParen) and (reference[i] == " "):
        formattedReference += " " + reference[i + 1].capitalize()   # Capitalize first char of each name
        i += 2
        continue

    if i in range(0, firstParen):
        formattedReference += reference[i].lower()
        i += 1
        continue

    if i in range(lastParen, titleEnd): # Format the title correctly
        if i == titleBeg:
            formattedReference += reference[i].capitalize()   # Capitlize the first char of title
            i += 1
        else:
            formattedReference += reference[i].lower()  # Convert everything else to lower
            i += 1

        continue    # Don't want to execute the rest of this iteration

    formattedReference += reference[i]  # No format changes required here
    i += 1

print("Reformatted reference:\n" + formattedReference)
