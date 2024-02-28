import random

ROCK = "Rock"
PAPER = "Paper"
SCISSORS = "Scissors"
WINNING_PAIRS = { (ROCK, SCISSORS), (PAPER, ROCK), (SCISSORS, PAPER) }

def ComputeChoice() -> str:
    rndIndex = random.randint(1, 3) # In python this function is inclusive of the upper-bound

    match rndIndex:
        case 1: return ROCK
        case 2: return PAPER
        case 3: return SCISSORS
        case _: return "ERROR"

if __name__ == "__main__":
    print(f"{ROCK}, {PAPER}, {SCISSORS}!")
    print("=========================================================")

    userChoice = input(f"Enter your choice: {ROCK}, {PAPER} or {SCISSORS}: ")
    computerChoice = ComputeChoice()

    print("=========================================================")
    print(f"Your choice: {userChoice}")
    print(f"My choice: {computerChoice}")

    if (userChoice == computerChoice):
        print("It's a tie!")
        exit()

    if ((userChoice, computerChoice) in WINNING_PAIRS):
        print("You won!")
    else:
        print("You lost!")
