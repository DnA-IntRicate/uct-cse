INCLUDE = include
SRC		= src
BIN_DIR	= bin

CXX		= g++
FLAGS	= -std=c++20 -I$(INCLUDE)

all: driver
	$(BIN_DIR)/driver

driver: factorial.o driver.o | $(BIN_DIR)
	$(CXX) $(BIN_DIR)/factorial.o $(BIN_DIR)/driver.o -o $(BIN_DIR)/driver $(FLAGS)

factorial.o: $(SRC)/factorial.cpp | $(BIN_DIR)
	$(CXX) -c $(SRC)/factorial.cpp -o $(BIN_DIR)/factorial.o $(FLAGS)

driver.o: $(SRC)/driver.cpp | $(BIN_DIR)
	$(CXX) -c $(SRC)/driver.cpp -o $(BIN_DIR)/driver.o $(FLAGS)

$(BIN_DIR):
	mkdir $(BIN_DIR)

clean:
	rm -rf $(BIN_DIR)

