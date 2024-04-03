# FFLADA001
# Prac Test 2A
# 02/04/24

numbers = []

inNumber = ""
while inNumber != "DONE":
    inNumber = input("Enter a number (or 'DONE' to End):\n")
    if inNumber == "DONE":
        break

    numbers.append(int(inNumber))

count = 0
sum = 0
i = 0

if numbers:
    while i < len(numbers) - 1:
        if (numbers[i] % 4 == 0) and (numbers[i + 1] % 4 == 0):
            count += 1
            sum += numbers[i] + numbers[i + 1]

        i += 1

print(f"Number of adjacent pairs of multiples of 4: {count}.")
print(f"Sum of adjacent pairs of multiples of 4: {sum}.")
