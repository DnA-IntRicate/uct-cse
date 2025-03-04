JAVA = java
JAVAC = javac
JAVADOC = javadoc

SRC_DIR = src
BIN_DIR = bin
DOC_DIR = doc

SOURCE_FILES = $(wildcard $(SRC_DIR)/*.java)
TARGET_NAMES = $(SOURCE_FILES:$(SRC_DIR)/%.java=$(BIN_DIR)/%.class)

# Default target
all: run

run: build
	cd ./$(BIN_DIR) && $(JAVA) GenericsKbArrayApp

build: $(TARGET_NAMES)
$(BIN_DIR)/%.class: $(SRC_DIR)/%.java
	@mkdir -p $(BIN_DIR)
	$(JAVAC) -d $(BIN_DIR) $(SOURCE_FILES)

# Post-build options
	@cp -r KnowledgeBases $(BIN_DIR)/

# I just like removing the whole directory :)
# My .gitignore file in the root of my repository also ignores bin folders
clean:
	@rm -rf $(BIN_DIR)
	@rm -rf $(DOC_DIR)

doc:
	$(JAVADOC) -d $(DOC_DIR) $(SOURCE_FILES)

