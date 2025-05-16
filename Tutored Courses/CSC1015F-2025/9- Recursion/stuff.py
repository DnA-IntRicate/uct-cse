def PrintNums(lst):
    if len(lst) == 0:
        return

    print(lst[0])
    PrintNums(lst[1:])

# Main
lst = [1, 2, 3, 4, 5, 6]
PrintNums(lst)
