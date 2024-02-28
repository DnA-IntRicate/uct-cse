rows = eval(input("Enter number of rows:\n"))

for i in range(1, rows + 1):
    lineBuf = ""
    numStars = (i * 2) - 1
    numSpaces = (rows - i)

    for j in range(0, numStars):
        lineBuf += "*"

    for j in range(1, numSpaces + 1):
        lineBuf = " " + lineBuf + " "

    print(lineBuf)
