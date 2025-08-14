CXX = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -I .

TARGET = ImageCompare
SRC = Main.cpp

BIN_DIR = ../bin
OUT_DIR = $(BIN_DIR)/$(TARGET)
OBJ_DIR = $(OUT_DIR)/intermediate

OBJ = $(patsubst %.cpp, $(OBJ_DIR)/%.o, $(SRC))

all: $(OUT_DIR)/$(TARGET)

# Bin directory
$(OUT_DIR)/$(TARGET): $(OBJ) | $(OUT_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Intermediate directory
$(OBJ_DIR)/%.o: %.cpp | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

$(OUT_DIR):
	mkdir -p $(OUT_DIR)

run: $(OUT_DIR)/$(TARGET)
	./$< $(ARGS)

clean:
	rm -rf $(OBJ_DIR) $(OUT_DIR)
