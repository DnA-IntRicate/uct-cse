package liftsim;

import javax.swing.*;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

/** Swing visual simulation with passengers WAITING on floors until their lift arrives. */
public class LiftSimulation {
	
	public static class Building {
	    public final int floors, elevators;
	    public final long travelMs, doorMs;

	    public final LiftMonitor liftController;  // per floor panel
	  
	    public Building(int floors, int elevators, long travelMs, long doorMs) {
	        this.floors = Math.max(2, floors);
	        this.elevators = Math.max(1, elevators);
	        this.travelMs = travelMs;
	        this.doorMs = doorMs;
	        this.liftController = new LiftMonitor(floors,elevators);
	       // for (int f = 0; f < floors; f++) liftButtons[f] = new FloorLiftButtons(f);
	    }
	}
	
    public static void main(String[] args) throws Exception {
         int liftCalls=50;
         int nlifts=7, nfloors =12;

        /* Read argument values */
        if (args.length==3) {  
        	 try {
		        nlifts=Integer.parseInt( args[0] );
		        if (nlifts <= 0) throw new IllegalArgumentException("Lifts must be greater than 0.");
		             
		        nfloors=Integer.parseInt( args[1] );
		       	if (nfloors <= 0) throw new IllegalArgumentException("Floors must be greater than 0.");
		       	
		       	
		     	liftCalls=Integer.parseInt( args[2] );
		     	if (liftCalls <= 0)  throw new IllegalArgumentException("Passengers must be greater than 0.");

	         } catch (NumberFormatException e) {
	             System.err.println("!!! Error: All arguments must be numeric.");
	             System.exit(1);
	         } catch (IllegalArgumentException e) {
	             System.err.println("!!! Error: " + e.getMessage());
	             System.exit(1);
	         }
         }
     
        Building b = new Building(nfloors, nlifts, 300, 400);
        
     	//create and start lift threads
     	Lift [] lifts = new Lift[b.elevators];
        for (int i = 0; i < b.elevators; i++) {
            lifts[i]= new Lift(i, b.floors,b.travelMs,b.doorMs,b.liftController);
            lifts[i].start();
        }
        
        //create and start passenger generating thread
        Passengers  passengers = new Passengers(b.liftController,liftCalls,3500);
        passengers.start(); //passengers only generated once start button pressed.
 
        //-------This does all the visualisation 
            JFrame f = new JFrame("Lift Simulation");
            View view = new View(b.floors, b.elevators, b.liftController);
            f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
           JPanel buttons = new JPanel();
            buttons.setLayout(new BoxLayout(buttons, BoxLayout.LINE_AXIS)); 
            
            JButton startB = new JButton("Start");  // the start button   		
    		startB.addActionListener(new ActionListener() {// add the listener to the jbutton to handle the "pressed" event
    		    public void actionPerformed(ActionEvent e)  {
    			    	  	b.liftController.startButtonPress();   //this is what happens when a button is pressed
    		    }
    		   });
    	
    		JButton endB = new JButton("Quit");
    				// add the listener to the jbutton to handle the "pressed" event
    				endB.addActionListener(new ActionListener() {
    			      public void actionPerformed(ActionEvent e) {
    			    	  System.exit(0);
    			      }
    			    });

    		buttons.add(view);
    		buttons.add(startB);
    		buttons.add(endB);
    		f.add(buttons);
            f.pack();
            f.setLocationByPlatform(true);
            f.setVisible(true);
    		//start viewer thread
    		Thread viewer = new Thread(view); 
    		viewer.start();
        //-----------------end vis---------------------------------

       System.out.println("---- Lift simulation  with "+liftCalls+" passengers. ----");   	 	    
    	     
       b.liftController.waitTillStartButtonPressed(); //wait until start button is pressed.

       passengers.join();
       b.liftController.setDone();
       for (int i = 0; i < b.elevators; i++) lifts[i].interrupt(); //interrupt waiting threads
       for (int i = 0; i < b.elevators; i++) lifts[i].join(); //interrupt waiting threads
   	   System.out.println("---- Lift simulation  complete. ----");   
   	   System.out.println(liftCalls+" passengers, "+ b.liftController.getnTrips()+ " trips");   
   	   
   	   //System.exit(0);
     
    }
}
