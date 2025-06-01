def CountOccurrence(lst, num):
    if len(lst) == 0:
        return 0
    
    if lst[0] == num:
        return 1 + CountOccurrence(lst[1:], num)

    return CountOccurrence(lst[1:], num)


nums = list(map(int, input("Enter stuff:\n").split()))
num = int(input("FIND ME: "))

print(CountOccurrence(nums, num))

