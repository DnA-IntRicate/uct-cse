# Adam Foflonker
# FFLADA001


print("Welcome to the Biology Expert")
print("-----------------------------")
print("Answer the following questions by selecting from among the options.")

skeleton = input("The skeleton is (internal/external)?\n")
if skeleton == "external":
    print("Type of animal: Arthropod")
    exit()

fertilisation = input("The fertilisation of eggs occurs (within the body/outside the body)?\n")
if fertilisation == "outside the body":
    habitat = input("It lives (in water/near water)?\n")
    if habitat == "in water":
        print("Type of animal: Fish")
    else:
        print("Type of animal: Amphibian")
    exit()

offspring = input("Young are produced by (waterproof eggs/live birth)?\n")
if (offspring == "live birth") and (fertilisation == "within the body"):
    print("Type of animal: Mammal")
    exit()

if offspring == "waterproof eggs":
    skin = input("The skin is covered by (scales/feathers)?\n")
    if skin == "scales":
        print("Type of animal: Reptile")
    else:
        print("Type of animal: Bird")
