package liftsim;

import java.util.Arrays;

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
        m_LiftStatuses = new LiftStatus[m_Lifts];
        m_Positions = new int[m_Lifts];
        m_Destinations = new int[m_Lifts];
        m_FloorsWaiting = new boolean[m_Floors];

        Arrays.fill(m_LiftStatuses, LiftStatus.IDLE);
        Arrays.fill(m_Positions, 0);
        Arrays.fill(m_Destinations, -1);
        Arrays.fill(m_FloorsWaiting, false);
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
                return;
            }
        }
    }

    public synchronized void callLift(int floor)
    {
        if ((floor < 0) || (floor >= m_Floors)) // Just in-case
            return;

        m_FloorsWaiting[floor] = true;
        while (!m_IsDone)
        {
            int bestLift = -1;
            int bestDistance = Integer.MAX_VALUE;

            for (int i = 0; i < m_Lifts; ++i)
            {
                if (m_LiftStatuses[i] == LiftStatus.IDLE)
                {
                    int distance = Math.abs(m_Positions[i] - floor);
                    if (distance < bestDistance)
                    {
                        bestDistance = distance;
                        bestLift = i;
                    }
                }
            }

            if (bestLift >= 0)
            {
                m_LiftStatuses[bestLift] = LiftStatus.INTRANSIT;
                m_Destinations[bestLift] = floor;
                notifyAll();

                return;
            }

            // No idle lift available - wait to be notified
            try
            {
                wait();
            }
            catch (InterruptedException ie)
            {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }

    public synchronized void setStatus(int id, LiftStatus status)
    {
        if ((id < 0) || (id >= m_Lifts))
            return;

        m_LiftStatuses[id] = status;
        notifyAll();
    }

    public synchronized LiftStatus status(int id)
    {
        if ((id < 0) || (id >= m_Lifts))
            return LiftStatus.IDLE;

        return m_LiftStatuses[id];
    }

    public synchronized void setDone()
    {
        m_IsDone = true;
        notifyAll();
    }

    public synchronized void updateLiftPosition(int id, int currentFloor)
    {
        if ((id < 0) || (id >= m_Lifts))
            return;

        m_Positions[id] = currentFloor;
    }

    public synchronized int getLiftPosition(int id)
    {
        if ((id < 0) || (id >= m_Lifts))
            return -1;

        return m_Positions[id];
    }

    public synchronized int destination(int id)
    {
        if ((id < 0) || (id >= m_Lifts))
            return -1;

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
                wait();
            }
            catch (InterruptedException ie)
            {
                Thread.currentThread().interrupt();
                return -1;
            }
        }

        return -1;
    }

    public synchronized void passengerCollected(int currentFloor, int id, int dest)
    {
        if ((id < 0) || (id >= m_Lifts))
            return;

        m_FloorsWaiting[currentFloor] = false;
        m_LiftStatuses[id] = LiftStatus.INUSE;
        m_Destinations[id] = dest;

        notifyAll();
    }

    public synchronized void passengerDelivered(int id)
    {
        if ((id < 0) || (id >= m_Lifts))
            return;

        m_Destinations[id] = -1;
        m_LiftStatuses[id] = LiftStatus.IDLE;
        m_TripCount++;

        notifyAll();
    }

    public synchronized boolean passengerWaiting(int floor)
    {
        if ((floor < 0) || (floor >= m_Floors))
            return false;

        return m_FloorsWaiting[floor];
    }

    public synchronized boolean isDone() { return m_IsDone; }
    public synchronized int getnTrips() { return m_TripCount; }
    public int getFloors() { return m_Floors; }

    private final int m_Floors;
    private final int m_Lifts;

    // parallel arrays
    private final LiftStatus[] m_LiftStatuses;
    private final int[] m_Positions;
    private final int[] m_Destinations;
    private final boolean[] m_FloorsWaiting;

    private boolean m_StartPressed = false;
    private boolean m_IsDone = false;
    private int m_TripCount = 0;
}
