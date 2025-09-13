package liftsim;

import java.util.*;
import java.util.concurrent.*;

/**
 * Monitors lifts, or something...
 *
 * @author Adam Foflonker (FFLADA001)
 */
public class LiftMonitor
{
    public enum LiftStatus
    {
        IDLE,
        INTRANSIT,
        INUSE
    }

    public LiftMonitor(int floors, int lifts)
    {
        m_Floors = floors;
        m_Lifts = lifts;
        m_LiftStatuses = new LiftStatus[m_Lifts]; Arrays.fill(m_LiftStatuses, LiftStatus.IDLE);
        m_Positions = new int[m_Lifts]; Arrays.fill(m_Positions, 0);
        m_Destinations = new int[m_Lifts]; Arrays.fill(m_Destinations, -1);
        m_FloorsWaiting = new boolean[m_Floors]; Arrays.fill(m_FloorsWaiting, false);
        m_FjPool = new ForkJoinPool();
    }

    public synchronized void startButtonPress()
    {
        m_StartPressed = true;
        notifyAll();
    }

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
                Thread.currentThread().interrupt();
            }
        }
    }

    public void callLift(int floor)
    {
        synchronized (this)
        {
            m_FloorsWaiting[floor] = true;
        }

        m_FjPool.execute(new LiftCallAction(floor));
    }

    public void setStatus(int id, LiftStatus status)
    {
        m_LiftStatuses[id] = status;
    }

    public LiftStatus status(int id)
    {
        return m_LiftStatuses[id];
    }

    public synchronized void setDone()
    {
        m_IsDone = true;
        notifyAll();
    }

    public void updateLiftPosition(int id, int currentFloor)
    {
        m_Positions[id] = currentFloor;
    }

    public int getLiftPosition(int id)
    {
        return m_Positions[id];
    }

    public int destination(int id)
    {
        return m_Destinations[id];
    }

    public synchronized int waitTillCalled(int id)
    {
        while (!m_IsDone)
        {
            int dest = m_Destinations[id];
            if (dest >= 0)
            {
                m_Destinations[id] = -1;
                return dest;
            }

            try
            {
                wait(); // Releases lock and waits until notifyAll() called
            }
            catch (InterruptedException ie)
            {
                Thread.currentThread().interrupt();
                return -1;
            }
        }

        return -1; // simulation done
    }

    public synchronized void passengerCollected(int currentFloor, int id, int dest)
    {
        m_LiftStatuses[id] = LiftStatus.INUSE;
        m_Destinations[id] = dest;
        notifyAll();
    }

    public synchronized void passengerDelivered(int id)
    {
        m_LiftStatuses[id] = LiftStatus.IDLE;
        m_TripCount++;
        notifyAll();
    }

    public boolean passengerWaiting(int floor)
    {
        return m_FloorsWaiting[floor];
    }

    public boolean isDone() { return m_IsDone; }
    public int getnTrips() { return m_TripCount; }
    public int getFloors() { return m_Floors; }

    private class LiftCallAction extends RecursiveAction
    {
        public LiftCallAction(int floor)
        {
            m_Floor = floor;
        }

        @Override
        protected void compute()
        {
            int assignedLift = -1;
            synchronized (LiftMonitor.this)
            {
                while (!m_IsDone && (assignedLift < 0))
                {
                    for (int i = 0; i < m_Lifts; ++i)
                    {
                        if (m_LiftStatuses[i] == LiftStatus.IDLE)
                        {
                            assignedLift = i;
                            m_LiftStatuses[i] = LiftStatus.INTRANSIT;
                            m_Destinations[i] = m_Floor;
                            m_FloorsWaiting[m_Floor] = false;
                            LiftMonitor.this.notifyAll();
                            break;
                        }
                    }

                    if (assignedLift < 0)
                    {
                        try
                        {
                            LiftMonitor.this.wait();
                        }
                        catch (InterruptedException e)
                        {
                            Thread.currentThread().interrupt();
                        }
                    }
                }
            }
        }

        private int m_Floor;
    }

    private int m_Floors = 0;
    private int m_Lifts = 0;

    // These 3 arrays are parallel
    private LiftStatus[] m_LiftStatuses;
    private int[] m_Positions;
    private int[] m_Destinations;

    private boolean[] m_FloorsWaiting;

    private ForkJoinPool m_FjPool;

    private boolean m_StartPressed = false;
    private boolean m_IsDone = false;
    private int m_TripCount = 0;
}
