import java.util.concurrent.CountDownLatch;
import java.util.concurrent.*;
import java.util.*;

//This is the class you have to fix
// You do not need to do anything when catching an interruption.

public class LiftMonitor {
   
    public enum LiftStatus { IDLE,INTRANSIT,INUSE}
   
   //logs of simulation state - for visualiser
    private boolean [] floorButtonPressed, passengerWaiting; //one for each floor
    private LiftStatus [] liftStatus;
    private int [] liftPositions, liftDestinations;
    
    //counters
    private int nCalls;
    private int nTrips;
    private int floors;
    private boolean done = false;
    private boolean m_StartPressed = false;
    
    //constructor - do not change the constructor
    public LiftMonitor(int floors, int lifts) { 
       this.floors = floors;
       floorButtonPressed = new boolean[floors];
       passengerWaiting = new boolean[floors];
       liftPositions = new int[lifts];
       liftStatus= new LiftStatus[lifts];
       liftDestinations = new int[lifts];
        
       for (int i=0;i<floors;i++) {
          floorButtonPressed[i]=false;
          passengerWaiting[i]=false;
       }
       for (int i=0;i<lifts;i++) {
          liftPositions[i]=0;
          liftStatus[i]=LiftStatus.IDLE;//idle
          liftDestinations[i]=-1;
       }
       nCalls=0;
       nTrips=0;
     }

  //lifts use this 
    public synchronized void waitTillStartButtonPressed()
    {
      while (!m_StartPressed)
      {
            try
            {
               wait();
            }
            catch (InterruptedException ie)
            {
               // Thread.currentThread().interrupt();
               return;
            }
      }
    }
    
    //button press uses this 
    public synchronized void startButtonPress()   
    {
      m_StartPressed = true;
      notifyAll();
    }

    
    //lifts use this
    public synchronized int waitTillCalled(int lift) 
    {
   while (nCalls == 0)
   {
      try { wait(); } catch (InterruptedException ie) { break; }
   }

        if ((nCalls <=0)&&(!isDone()))
        {
             liftStatus[lift]=LiftStatus.IDLE;//idle
         }   
       for (int i=0;i<floors;i++) {
              if (floorButtonPressed[i]==true) {
                     floorButtonPressed[i]=false;
                     nCalls--;
                     liftStatus[lift]=LiftStatus.INTRANSIT;
                     return i;
                  }
          }

          return -1;   // just in case
    }
    
    //passengers use this
    public synchronized void callLift(int floor)   
    {
       if((floor>=0) &&(floor<floors))
       {
           nCalls++;
           floorButtonPressed[floor]=true;
           passengerWaiting[floor]=true;
      notifyAll();
        }
    }
    
  //lift users this 
    public synchronized void passengerCollected (int floor, int lift, int dest) {
       passengerWaiting[floor]=false;
       liftStatus[lift]=LiftStatus.INUSE;
       liftDestinations[lift]=dest;

       notifyAll();
    }

    //lift users this 
    public synchronized void passengerDelivered (int lift) {
       nTrips++;
       liftStatus[lift]=LiftStatus.IDLE;

       notifyAll();
    }

    //for lift, after it has moved, update log
    public synchronized void updateLiftPosition(int lift, int floor) {
        liftPositions[lift]=floor;
    }
    
    //setter
   public synchronized void setDone() {
      this.done = true;
   }
   
    //getter - for viewer
    public synchronized int getLiftPosition(int lift) {
       return  liftPositions[lift];
    }
    
    //getter
    public synchronized LiftStatus status(int lift) {
       return  liftStatus[lift];
    }
    
    //getter 
    public synchronized int destination(int lift) {
       return  liftDestinations[lift];
    }
    
    //setter
    public synchronized void setStatus(int lift,LiftStatus status) {
        liftStatus[lift]=status;
    }
    
    //getter
    public synchronized boolean passengerWaiting (int floor) {
       return  passengerWaiting[floor];
    }
    
   //getter
   public synchronized int getFloors() {
      return floors;
   }

   //getter
   public synchronized int getnTrips() {
      return nTrips;
   }

   //getter
   public synchronized boolean isDone() {
      return done;
   } 
 }