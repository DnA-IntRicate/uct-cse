# Adam Foflonker
# FFLADA001
# 30/04/24
# Practical Test 3J

def count_substrings(main_string, char):
    """
    Function to count the occurrences of substrings starting with a certain character in a given string.

    Args:
    main_string (str): The main string in which occurrences will be counted.
    char (str): The character to check for at the beginning of substrings.

    Returns:
    int: The count of substrings starting with the specified character.
    """

    res = 0
    char = char.lower()

    strings = main_string.split()
    for s in strings:
        s = s.lower()
        if char in s:
            res += s.count(char)

    return res

def find_all_substrings(main_string, char):
    """
    Function to find all substrings starting with a certain character in a given string.

    Args:
    main_string (str): The main string in which occurrences will be found.
    char (str): The character to check for at the beginning of substrings.

    Returns:
    list: A list containing the substrings starting with the specified character.
    """

    res = []
    main_string = main_string.lower()
    char = char.lower()

    index = main_string.find(char)
    while index != -1:
        res.append(main_string[index:])

        index = main_string.find(char, index + 1)

    return res

def main():
    """
    Main function to accept input and print out results.
    """
    main_string = input("Enter the main string:\n")
    starting_char = input("Enter the character to search for at the beginning of substrings:\n")

    count = count_substrings(main_string, starting_char)
    print("Number of substrings starting with '{}': {}".format(starting_char, count))

    substrings = find_all_substrings(main_string, starting_char)
    if substrings:
        print("Substrings starting with '{}':".format(starting_char))
        print(", ".join(substrings))
    else:
        print("No substrings starting with '{}' found.".format(starting_char))

if __name__ == "__main__":
    main()
