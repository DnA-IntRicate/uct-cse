# Assignment 3B
# biology.py Sample Solution
# Adam Foflonker
# 09/03/25

print("Welcome to the Biology Expert")
print("------------------------------------------------------------------")
print("Answer the following questions by selecting from among the options.")

if input("Does the organism have a backbone? (yes/no):\n").lower() == "yes":
    if input("Is it warm-blooded? (yes/no):\n").lower() == "yes":
        if input("Does it have feathers? (yes/no):\n").lower() == "yes":
            print("It is a Bird.")
        elif input("Does it have fur? (yes/no):\n").lower() == "yes":
            print("It is a Mammal.")
        else:
            print("It is an Other vertebrate.")
    elif input("Does it have scales? (yes/no):\n").lower() == "yes":
        if input("Does it live in water? (yes/no):\n").lower() == "yes":
            print("It is a Fish.")
        else:
            print("It is a Reptile.")
    else:
        print("It is an Amphibian.")
elif input("Does it have an exoskeleton? (yes/no):\n").lower() == "yes":
    if input("Does it have six legs? (yes/no):\n").lower() == "yes":
        print("It is an Insect.")
    elif input("Does it have eight legs? (yes/no):\n").lower() == "yes":
        print("It is an Arachnid.")
    else:
        print("It is a Crustacean.")
elif input("Does it have a segmented body? (yes/no):\n").lower() == "yes":
    print("It is an Annelid (e.g., Earthworm).")
elif input("Does it have a shell? (yes/no):\n").lower() == "yes":
    print("It is a Snail or Clam.")
else:
    print("It is an Octopus or Squid.")
