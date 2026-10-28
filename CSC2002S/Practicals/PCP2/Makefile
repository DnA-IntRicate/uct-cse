
JAVAC=javac
JAVA=java
SRC=liftsim
CLASSES = $(SRC)/Lift.java $(SRC)/LiftMonitor.java $(SRC)/Passengers.java $(SRC)/View.java $(SRC)/LiftSimulation.java

# Default arguments (update these if needed)
ARGS ?= 7 12 50  # Replace 'default_arguments' with your specific default arguments, if any


all:
	$(JAVAC) $(CLASSES)	

run: all
	$(JAVA) liftsim.LiftSimulation $(ARGS) 
	
clean:
	rm -f $(SRC)/*.class
