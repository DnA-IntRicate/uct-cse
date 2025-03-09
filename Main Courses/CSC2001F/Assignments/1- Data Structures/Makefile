JAVA = java
JAVAC = javac
JAVADOC = javadoc

SRC_DIR = src
BIN_DIR = bin
DOC_DIR = doc

SOURCE_FILES = $(wildcard $(SRC_DIR)/*.java)
TARGET_NAMES = $(SOURCE_FILES:$(SRC_DIR)/%.java=$(BIN_DIR)/%.class)

# Default target
all: build

array: build
# Explicitly changing working-dir to the bin folder
	cd ./$(BIN_DIR) && $(JAVA) GenericsKbArrayApp

bst: build
# Explicitly changing working-dir to the bin folder
	cd ./$(BIN_DIR) && $(JAVA) GenericsKbBSTApp

build: $(TARGET_NAMES)
$(BIN_DIR)/%.class: $(SRC_DIR)/%.java
	@mkdir -p $(BIN_DIR)
	$(JAVAC) -d $(BIN_DIR) $(SOURCE_FILES)

# Post-build options
	@cp KnowledgeBases/GenericsKB.txt $(BIN_DIR)/
	@cp KnowledgeBases/GenericsKB-additional.txt $(BIN_DIR)/

clean:
	@rm -rf $(BIN_DIR)
	@rm -rf $(DOC_DIR)

doc:
	$(JAVADOC) -d $(DOC_DIR) $(SOURCE_FILES)
