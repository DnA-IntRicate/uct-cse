# Define the compiler and flags
HC = ghc
HCFLAGS = -O2 -Wall

# Define targets
TARGET = baseGame
SRC = baseGame.hs

all: $(TARGET)

$(TARGET): $(SRC)
	$(HC) $(HCFLAGS) $(SRC) -o $(TARGET)

# NOTE(Adam): I wrote this on windows!
run:
	$(TARGET).exe

clean:
	rm -f *.o *.hi $(TARGET)

.PHONY: all run clean
