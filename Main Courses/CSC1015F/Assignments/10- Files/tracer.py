# Adam Foflonker
# FFLADA001
# 25/04/24
# Tracing Python source files

DEBUG_MARKER: str = "\"\"\"DEBUG\"\"\""

# Returns true if s is a valid Python function header
def IsFunctionHeader(s: str) -> bool:
    if not s:
        return False

    return s[:3] == "def" # This is not the best way to do this, but for this scenario it works

# Returns the function name from a function header
def FunctionNameFromHeader(header: str) -> str:
    return header[4:header.find('(')].strip()

# Returns the index of the first char not equal to c in s. Returns -1 if there are none
def FindFirstNotOf(s: str, c: str) -> int:
    for i in range(len(s)):
        if s[i] != c:
            return i

    return -1

# Returns true if src contains trace statements
def HasTraceStatements(src: list[str]) -> bool:
    return DEBUG_MARKER in src[0]

# Returns a new list with trace statements inserted
def InsertTraceSatements(src: list[str]) -> list[str]:
    newSource = []
    i = 0
    while i < len(source):
        newSource.append(source[i])

        if IsFunctionHeader(source[i]):
            funcName = FunctionNameFromHeader(source[i])
            indentation = source[i + 1][:FindFirstNotOf(source[i + 1], ' ')]    # Preserve indentation
            newSource.append(f"{indentation}{DEBUG_MARKER};print('{funcName}')\n")

        i += 1

    return [f"{DEBUG_MARKER}\n"] + newSource

# Returns a new list with all trace statements removed
def RemoveTraceStatements(src: list[str]) -> list[str]:
    newSource = []
    for line in src:
        if DEBUG_MARKER not in line:
            newSource.append(line)

    return newSource

if __name__ == "__main__":
    print("***** Program Trace Utility *****")
    filePath = input("Enter the name of the program file:\n")

    file = open(filePath, 'r+')
    source = file.readlines()

    if HasTraceStatements(source):
        print("Program contains trace statements\nRemoving...", end='')
        source = RemoveTraceStatements(source)
    else:
        print("Inserting...", end='')
        source = InsertTraceSatements(source)

    file.seek(0)
    file.writelines(source)
    file.truncate()
    file.close()
    print("Done")
