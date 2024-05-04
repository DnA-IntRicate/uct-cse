# Adam Foflonker
# FFLADA001
# 03/05/24
# A simple contact manager using a text file with CSV formatting

from os import path
from copy import deepcopy

# Contacts are stored in CSV format in the contacts file
CONTACT_DELIM: str = ','

# The index of the name of the contact in the two-dimensional contacts list
IDX_NAME: int = 0

# The index of the phone number of the contact in the two-dimensional contacts list
IDX_PHONE: int = 1

# The index of the email address of the contact in the two-dimensional contacts list
IDX_EMAIL: int = 2

# Returns true if file_path exists
def path_exists(file_path: str) -> bool:
    return path.exists(file_path)

# Returns a list of contacts read from the contacts file at file_path
def read_contacts(file_path: str) -> list[list[str]]:
    file = open(file_path, 'r')

    res: list[list[str]] = []
    for line in file.readlines():
        if line == '\n':
            continue

        line = line.strip()
        res.append(line.split(CONTACT_DELIM))

    file.close()

    return res

# Add a new contact to the contacts file. Does not add if the contact already exists. Returns a completion message
def add_contact(file_path: str, name: str, phone: str, email: str) -> str:
    contacts = read_contacts(file_path)
    for contact in contacts:
        if (name in contact) or (phone in contact) or (email in contact):
            return "Contact already exists."

    contactsFile = open(file_path, 'a')
    contactsFile.write(f"{name},{phone},{email}\n")
    contactsFile.flush()
    contactsFile.close()

    return "Contact added successfully."

# Returns contacts in a formatted grid as a string
def generate_contact_grid(contacts: list[list[str]]) -> str:
    res = "============================================================\n"
    res += f"| {'Name'.ljust(21)}| {'Phone'.ljust(16)}| {'Email'.ljust(26)}|\n"
    res += "============================================================\n"

    for contact in contacts:
        name = contact[IDX_NAME]
        phone = contact[IDX_PHONE]
        email = contact[IDX_EMAIL]

        res += f"| {name.ljust(21)}| {phone.ljust(16)}| {email.ljust(26)}|\n"
        res += "------------------------------------------------------------\n"

    return res[:-1] # NOTE: Here we remove the last extra newline character from the end of the grid

# Returns a copy of lst bubble sorted in ascending order
def sort_ascending(lst: list[str]) -> list[str]:
    res = deepcopy(lst)

    for i in range(len(res)):
        for j in range(len(res) - i - 1):
            if res[j] > res[j + 1]:
                res[j], res[j + 1] = res[j + 1], res[j]

    return res

# Returns a copy of contacts bubble sorted alphabetically on IDX_NAME
def custom_sort(contacts: list[list[str]]) -> list[list[str]]:
    res = deepcopy(contacts)

    for i in range(len(res)):
        for j in range(len(res) - i - 1):
            if res[j][IDX_NAME] > res[j + 1][IDX_NAME]:
                res[j], res[j + 1] = res[j + 1], res[j]

    return res

# Returns true if query equals s or matches s when treated as an expression
def string_match(s: str, query: str) -> bool:
    return (s == query) or (query in s)

# Performs a ternary search/match on lst for query between left and right and returns its index. Returns -1 if not found
# lst MUST be sorted in ascending order
def ternary_search(lst: list[str], left: int, right: int, query: str) -> int:
    while right >= left:
        leftMid = left + ((right - left) // 3)
        rightMid = right - ((right - left) // 3)

        if string_match(lst[leftMid], query):
            return leftMid

        if string_match(lst[rightMid], query):
            return rightMid

        if lst[leftMid] > query:
            right = leftMid - 1
            continue

        if lst[rightMid] < query:
            left = rightMid + 1
            continue

        left = leftMid + 1
        right = rightMid - 1

    return -1

# Returns a list of all the indices in lst where query was found/matched using ternary search
def find_all_of(lst: list[str], query: str) -> list[int]:
    res: list[int] = []

    right = len(lst) - 1
    left = ternary_search(lst, 0, right, query)
    while left != -1:
        res.append(left)
        left = ternary_search(lst, left + 1, right, query)

    return res

# Returns a contact grid containing contacts matching the query from the contacts file at file_path using ternary search
def search_contact(file_path: str, query: str) -> str:
    sortedContacts = custom_sort(read_contacts(file_path))

    if query == '*':
        return "Found contact(s):\n" + generate_contact_grid(sortedContacts)

    # Create dicts matching unique contact details to their respective indices in sortedContacts to be used later
    sortedContactsNameIndexMap: dict[str, int] = {}
    sortedContactsPhoneNumberIndexMap: dict[str, int] = {}
    sortedContactsEmailAddressIndexMap: dict[str, int] = {}
    for i, contact in enumerate(sortedContacts):
        sortedContactsNameIndexMap[contact[IDX_NAME]] = i
        sortedContactsPhoneNumberIndexMap[contact[IDX_PHONE]] = i
        sortedContactsEmailAddressIndexMap[contact[IDX_EMAIL]] = i

    # Sort names, phone numbers and email addresses in ascending order separately for ternary searching
    sortedNames = [contact[IDX_NAME] for contact in sortedContacts]
    sortedPhoneNumbers = sort_ascending([contact[IDX_PHONE] for contact in sortedContacts])
    sortedEmailAddresses = sort_ascending([contact[IDX_EMAIL] for contact in sortedContacts])

    nameIndices = find_all_of(sortedNames, query)
    phoneNumberIndices = find_all_of(sortedPhoneNumbers, query)
    emailAddressIndices = find_all_of(sortedEmailAddresses, query)

    if (not nameIndices and not phoneNumberIndices and not emailAddressIndices):
        return "No contact found."

    searchedNames = [sortedNames[idx] for idx in nameIndices]
    searchedPhoneNumbers = [sortedPhoneNumbers[idx] for idx in phoneNumberIndices]
    searchedEmailAddresses = [sortedEmailAddresses[idx] for idx in emailAddressIndices]

    # Merge the 3 separate sets of search results into a singular two-dimensional list of contacts
    # NOTE: This approach was taken since a search query could potentially match with both a name and an email address
    searchResults: list[list[str]] = []

    for name in searchedNames:
        i = sortedContactsNameIndexMap[name]
        searchResults.append([name, sortedContacts[i][IDX_PHONE], sortedContacts[i][IDX_EMAIL]])

    for phoneNumber in searchedPhoneNumbers:
        i = sortedContactsPhoneNumberIndexMap[phoneNumber]
        searchResults.append([sortedContacts[i][IDX_NAME], phoneNumber, sortedContacts[i][IDX_EMAIL]])

    for emailAddress in searchedEmailAddresses:
        i = sortedContactsEmailAddressIndexMap[emailAddress]
        searchResults.append([sortedContacts[i][IDX_NAME], sortedContacts[i][IDX_PHONE], emailAddress])

    # Filter out any duplicates from searchResults and sort in alphabetical order
    # NOTE: Sets are used to filter out all duplicates however, since a set can only contain hashable types and lists
    #       are not hashable, they are converted to tuples first, then to sets and then back to lists to remove duplicates if any
    uniqueContactSet = set(tuple(contact) for contact in searchResults)
    uniqueContacts = custom_sort([list(contact) for contact in uniqueContactSet])

    return "Found contact(s):\n" + generate_contact_grid(uniqueContacts)

# Returns all contacts read from the contacts file at file_path sorted alphabetically by name in a formatted grid as a string
def list_contacts(file_path: str) -> str:
    contacts = custom_sort(read_contacts(file_path))

    return "List of contacts:\n" + generate_contact_grid(contacts)

def main():
    contactsPath = input("Enter the name for the contacts file:\n") + ".txt"
    if not path_exists(contactsPath):
        newFile = open(contactsPath, 'w')
        if newFile:
            print(f"Contacts file '{contactsPath}' created.")

        newFile.close()

    while True:
        print()
        print("1. Add Contact")
        print("2. Search Contact")
        print("3. List Contacts")
        print("4. Exit")
        option = eval(input("Enter your choice: "))

        match option:
            case 1:
                name = input("Enter name: ")
                phone = input("Enter phone number: ")
                email = input("Enter email: ")
                print(add_contact(contactsPath, name, phone, email))
            case 2:
                query = input("Enter first name, last name, phone number, or email to search:\n")
                print(search_contact(contactsPath, query))
            case 3:
                print()
                print(list_contacts(contactsPath))
            case 4:
                print("Exiting program." )
                break


if __name__ == "__main__":
    main()
