package liftsim;

import java.util.Random;

//Thread to generate random lift calls from "passengers'

public class Passengers extends Thread {
    private LiftMonitor liftMonitor;   
    private final int maxSleepMs;   
    private final Random rnd;
    private final int nPassengers;

    public Passengers(LiftMonitor liftMonitor, int nPassengers, int maxSleepMs) {
        this.liftMonitor = liftMonitor;
        this.maxSleepMs = maxSleepMs;
		this.nPassengers = nPassengers;
        this.rnd = new Random();
    }

    @Override public void run() {
        try {
        	int floors=liftMonitor.getFloors();
           	liftMonitor.waitTillStartButtonPressed(); //passengers also wait until start button is pressed.
            
            for (int i = 0; i < nPassengers; i++) {
                int floor = rnd.nextInt(floors);     // random floor
                liftMonitor.callLift(floor);         // call a lift
                System.out.println("call from floor " + floor);
                Thread.sleep(rnd.nextInt(maxSleepMs));
            }
        } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
        }
    }
}
