CC=g++ 					# Compiler
#CUSTOMDIR=/home/alice/local 		# Custom package location
#LIBDIRS=-L$(CUSTOMDIR)/libs 		# Library Locations
#INCLUDES=-I$(CUSTOMDIR)/includes 	# Header File Locations
#LIBS=-lalice # libalice.a
STD=-std=c++23
CXXFLAGS=$(INCLUDES) -fsanitize=leak -Wall $(STD) 	# Headers + All Warnings 	# -Wno-sign-compare
#LDFLAGS=$(LIBDIRS) $(LIBS) 		# Libs + their locations
TARGET=Assignment3			# Name of executable
OBJECTS=Assignment3.o 			# Object files

# Linking Rule
$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)
	@cp $(TARGET) ./binaries

# Macro: automatically associate *.o with *.cpp
.cpp.o:
	$(CC) $(CXXFLAGS) -c $<

clean:
	@rm -f *.o
