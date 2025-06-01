def get_consonants(s, index = 0) -> list[str]:
    if index > len(s) - 1:
        return []

    if s[index].lower() not in "aeiou":
        return [s[index]] + get_consonants(s, index + 1)

    return get_consonants(s, index + 1)

word = input("Enter word:\n")
print(get_consonants(word))
