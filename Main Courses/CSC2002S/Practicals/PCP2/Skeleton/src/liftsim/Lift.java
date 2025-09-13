package liftsim;

// This is the Lift class
// You may not change anything in this class.

import java.util.concurrent.ThreadLocalRandom;

public class Lift extends Thread {
    private final int id;
  
    public enum Direction { UP, DOWN }

    private long travelMs, doorMs;
    private int floors;
    private LiftMonitor liftController;		
 
    private int currentFloor = 0;
    private Direction travel = null; // null means idle

    public Lift(int id, int floors, long travelMS, long doorMS,LiftMonitor liftButtons) {
        this.id = id; 
        this.floors=floors;
        this.travelMs = travelMS;
        this.doorMs=doorMS;
        this.liftController= liftButtons;
	    liftController.setStatus(id, LiftMonitor.LiftStatus.IDLE); //lift waiting
    }

    public int id() { return id; }
    
    @Override public void run() {
    	
    		liftController.waitTillStartButtonPressed(); //only start after start button pressed
         	liftController.updateLiftPosition(id, currentFloor); //make sure lift position is updated for view thread
         	 boolean running=true;
            while (!liftController.isDone()) {
            	int dest=-1;
	            	while((dest<0)&&!liftController.isDone()) dest=liftController.waitTillCalled(id);
	            	if(dest>=0) {//double check
		                    System.out.println("---> Lift"+id+" called to "+dest);	 
							moveTo(dest);
				           	System.out.println("--- Lift"+id+" at "+dest);
			                doorCycle();
			                while(dest==currentFloor) dest= ThreadLocalRandom.current().nextInt(0, floors); //pressing button in lift, destination can't be current floor
			                liftController.passengerCollected(currentFloor,id,dest);
			                System.out.println("<--- Lift"+id+" sent to "+dest);
		                	moveTo(dest);
		                	doorCycle();
		                	liftController.passengerDelivered(id);
	            	 } 
              
            } 	   
            System.out.println("=== Lift"+id+" done===");	 

        }
  
    private void moveTo(int target)  {
        while (true) {
            int here = currentFloor; 
            if (here == target) break;
             travel = (target > here) ? Direction.UP : Direction.DOWN; 
             try {Thread.sleep(travelMs);}
             catch (InterruptedException e) {
     	       //do nothing if interrupted here - have to finish cycle 
             }
             if (travel == Direction.UP) currentFloor++;
             else currentFloor--;
             liftController.updateLiftPosition(id, currentFloor); //for visualizaiton
         }
    }

    private void doorCycle()  {
    	try {
        Thread.sleep(doorMs); // open
        Thread.sleep(20);       // dwell
        Thread.sleep(doorMs); // close
    	} catch (InterruptedException e) {}
   	       //do nothing if interrupted here - have to finish cycle 
     
    }

}  

   

