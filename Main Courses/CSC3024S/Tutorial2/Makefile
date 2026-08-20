SRC_DIR	:= .
TARGET := test

CXX         := g++
CXXFLAGS	:= -std=c++20 -Werror

SOURCES := DynamicArray.cpp
OBJECTS := DynamicArray.o

all: $(TARGET)

run: $(TARGET)
	./$(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@

$(OBJECTS): $(SOURCES)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -rf $(TARGET)

.PHONY: all run clean
