JAVA = java
JAVAC = javac
JAVADOC = javadoc

SRC_DIR = src
BIN_DIR = bin
DOC_DIR = doc

SOURCE_FILES = $(wildcard $(SRC_DIR)/*.java)
TARGET_NAMES = $(SOURCE_FILES:$(SRC_DIR)/%.java=$(BIN_DIR)/%.class)

# Command-line flags
USE_INSTRUMENTATION = 1

# Default target
all: build

run: build
# Explicitly changing working-dir to the bin folder
	cd ./$(BIN_DIR) && $(JAVA) GenericsKbAVLApp

instrumented: build
# Explicitly changing working-dir to the bin folder
# Passing a command-line arg to the app as a flag to enable instrumentation
	cd ./$(BIN_DIR) && $(JAVA) GenericsKbAVLApp $(USE_INSTRUMENTATION)

build: $(TARGET_NAMES)
$(BIN_DIR)/%.class: $(SRC_DIR)/%.java
	@mkdir -p $(BIN_DIR)
	$(JAVAC) -d $(BIN_DIR) $(SOURCE_FILES)

# Post-build options
	cp -r KnowledgeBases/ $(BIN_DIR)/
	cp -r TestData/ $(BIN_DIR)/
	@echo

clean:
	rm -rf $(BIN_DIR)
	rm -rf $(DOC_DIR)
	@echo

doc:
	$(JAVADOC) -d $(DOC_DIR) $(SOURCE_FILES)
