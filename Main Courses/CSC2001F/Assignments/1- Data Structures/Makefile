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
# Explicitly changing working-dir to the bin folder
	cd ./$(BIN_DIR) && $(JAVA) GenericsKbArrayApp

build: $(TARGET_NAMES)
$(BIN_DIR)/%.class: $(SRC_DIR)/%.java
	@mkdir -p $(BIN_DIR)
	$(JAVAC) -d $(BIN_DIR) $(SOURCE_FILES)

# Post-build options
	@cp -r KnowledgeBases $(BIN_DIR)/

clean:
	@rm -rf $(BIN_DIR)
	@rm -rf $(DOC_DIR)

doc:
	$(JAVADOC) -d $(DOC_DIR) $(SOURCE_FILES)
