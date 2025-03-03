JAVA = java
JAVAC = javac

SRC_DIR = src
BIN_DIR = bin
DOC_DIR = doc

SOURCE_FILES = $(wildcard $(SRC_DIR)/*.java)
TARGET_NAMES = $(SOURCE_FILES:$(SRC_DIR)/%.java=$(BIN_DIR)/%.class)

# Default target
all: build run

run: build
	$(JAVA) -cp $(BIN_DIR) ChatGPTLite

build: $(TARGET_NAMES)
$(BIN_DIR)/%.class: $(SRC_DIR)/%.java
	@mkdir -p $(BIN_DIR)
	$(JAVAC) -d $(BIN_DIR) $(SOURCE_FILES)

# Post-build options
	@cp -r KnowledgeBases $(BIN_DIR)/KnowledgeBases

# I just like removing the whole directory :)
# My .gitignore file in the root of my repository also ignores bin folders
clean:
	@rm -rf $(BIN_DIR)
