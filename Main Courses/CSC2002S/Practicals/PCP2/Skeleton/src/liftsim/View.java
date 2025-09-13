package liftsim;

//This class draws the view panel continuously.
// DO NOT CHANGE ANYTHING IN THIS FILE
import javax.swing.*;
import java.awt.*;

/** Draw floors, waiting passengers, and elevator cars + stops. */
public class View extends JPanel  implements Runnable {
    final int floorH = 20;
    final int triH= floorH/2;
    final int shaftW = 40;
    final int midP = shaftW/2;
    final int leftMargin = 120;
    final int leftOffset = leftMargin/2;
    final int topMargin = 20;

    private int floors;
    private int cars;
    LiftMonitor lifts;

    public View(int floors, int cars, LiftMonitor lifts) {
        this.floors = floors;
        this.cars = cars;
        this.lifts=lifts;
        setPreferredSize(new Dimension(200 + 70*cars, 24*floors));
        setBackground(Color.WHITE);
    }

    @Override protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        // Floors and labels
        g.setColor(Color.LIGHT_GRAY);
        for (int f = 0; f < floors; f++) {
            int y = (floors - 1 - f) * floorH+topMargin;
            g.drawLine(0, y, getWidth(), y);
            g.setColor(Color.DARK_GRAY);
            g.drawString("F" + f, 6, y + 15);
            g.setColor(Color.LIGHT_GRAY);
        }

        // Pending hall calls (waiting passengers) as counts + arrows
         for (int f = 0; f < floors; f++) {
            if (lifts.passengerWaiting(f))
            {
                int y = (floors - 1 - f) * floorH +topMargin;
                g.setColor(new Color(200,0,0));
                g.fillPolygon(new int[]{leftOffset+midP,leftOffset+midP+triH,leftOffset+midP}, new int[]{y, y+triH, y+triH*2}, 3); // red arrow
              }
        }

        // Draw Elevators and their car stops
        int floor;
        for (int l =0; l< cars; l++) {
            int x = leftMargin + l * 70;
            floor = lifts.getLiftPosition(l);
            int y = (floors - 1 - floor) * floorH+topMargin;
            if (lifts.status(l)==LiftMonitor.LiftStatus.IDLE)  {
            	g.setColor(new Color(200,200,200));
            	g.fillRect(x, y, shaftW, floorH);
            }
            else  if (lifts.status(l)==LiftMonitor.LiftStatus.INTRANSIT)
            	{
            	g.setColor(new Color(100,220,100));
            	g.fillRect(x, y, shaftW, floorH);
            	}
            else {//INUSE
            	g.setColor(new Color(250,100,100));
            	g.fillRect(x, y, shaftW, floorH);
            	g.setColor(new Color(250,250,250));
                g.fillPolygon(new int[]{x+midP,x+midP+triH,x+midP}, new int[]{y, y+triH, y+triH*2}, 3); // red arrow
                g.setColor(Color.WHITE);
                g.drawString(" "+lifts.destination(l) , x, y+floorH-2);
            }

            g.setColor(Color.BLACK);
            g.drawRect(x, y, shaftW, floorH);
            g.drawString("E" + l , x, y-4);

        }
    }
  //the thread just continually redraws the image
  		public void run() {
  			final int frameMs = 50; // ~20 FPS; use 16 for ~60, 100 for lighter load
  		    try {
  		        while (!Thread.currentThread().isInterrupted()) {
  		            repaint();          // thread-safe: posts a paint on the EDT
  		            Thread.sleep(frameMs);
  		        }
  		    } catch (InterruptedException ie) {

  		    }
  		}
}
