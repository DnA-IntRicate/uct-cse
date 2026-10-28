package SoloLeveling.Parallel;

import java.util.concurrent.RecursiveTask;

/**
 * Implementation of {@link SoloLeveling.Serial.Hunt} for use in {@link DungeonHunterParallel}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 15/08/2025
 */
public class HuntParallel extends RecursiveTask<Integer>
{
    /** Hunt directions */
    public enum Direction
    {
        Stay,
        Left,
        Right,
        Up,
        Down,
        UpLeft,
        UpRight,
        DownLeft,
        DownRight
    }

    /**
     * Creates a new {@link HuntParallel}.
     *
     * @param id the ID of the hunt
     * @param rowPos the row-index of the hunt
     * @param colPos the column-index of the hunt
     * @param dungeon the dungeon map to search inside of
     */
    public HuntParallel(int id, int rowPos, int colPos, final DungeonMapParallel dungeon)
    {
        super();

        m_ID = id;
        m_RowPos = rowPos;
        m_ColPos = colPos;
        m_Dungeon = dungeon;
        m_Stopped = false;
    }

    /** Allows {@link HuntParallel#FindManaPeak()} to be called concurrently on separate threads */
    @Override
    protected Integer compute()
    {
        return FindManaPeak();
    }

    /**
     * Find the local maximum mana from an initial starting point.
     *
     * @return the highest power/mana located
     */
    public int FindManaPeak()
    {
        int power = Integer.MIN_VALUE;
        Direction next = Direction.Stay;

        // Stop when hit existing path
        while(!m_Dungeon.Visited(m_RowPos, m_ColPos))
        {
            power = m_Dungeon.GetManaLevel(m_RowPos, m_ColPos);
            m_Dungeon.SetVisited(m_RowPos, m_ColPos, m_ID);

            m_Steps++;
            next = m_Dungeon.GetNextStepDirection(m_RowPos, m_ColPos);

            if(DungeonHunterParallel.DEBUG)
                System.out.println("Shadow "+ GetID() + " moving  " + next);

            switch(next)
            {
                case Stay: return power; // Found local valley
                case Left:
                    m_RowPos--;
                    break;
                case Right:
                    m_RowPos = m_RowPos + 1;
                    break;
                case Up:
                    m_ColPos = m_ColPos - 1;
                    break;
                case Down:
                    m_ColPos = m_ColPos + 1;
                    break;
                case UpLeft:
                    m_ColPos = m_ColPos - 1;
                    m_RowPos--;
                    break;
                case UpRight:
                    m_ColPos = m_ColPos - 1;
                    m_RowPos = m_RowPos + 1;
                    break;
                case DownLeft:
                    m_ColPos = m_ColPos + 1;
                    m_RowPos--;
                    break;
                case DownRight:
                    m_ColPos = m_ColPos + 1;
                    m_RowPos = m_RowPos + 1;
                    break;
            }
        }

        m_Stopped = true;
        return power;
    }

    /**
     * Returns this hunt's ID.
     *
     * @return this hunt's ID
     */
    public int GetID() { return m_ID; }

    /**
     * Returns this hunt's row position in the {@link DungeonMapParallel}.
     *
     * @return this hunt's row position in the dungeon map
     */
    public int GetRowPos() { return m_RowPos;}

    /**
     * Returns this hunt's column position in the {@link DungeonMapParallel}.
     *
     * @return this hunt's column position in the dungeon map
     */
    public int GetColPos() { return m_ColPos;}

    /**
     * Returns the number of steps to the end of this hunt.
     *
     * @return the number of steps to the end of this hunt
     */
    public int GetSteps() { return m_Steps;}

    /**
     * Did the search hit a previously searched location?
     *
     * @return {@code true} if this hunt stopped, {@code false} otherwise
     */
    public boolean IsStopped() {return m_Stopped;}

    // Identifier for this hunt
    private int m_ID = 0;

    // Row position in the dungeon map
    private int m_RowPos = 0;

    // Column position in the dungeon map
    private int m_ColPos = 0;

    // Number of steps to the end of the search
    private int m_Steps = 0;

    // The dungeon map
    private DungeonMapParallel m_Dungeon;

    // Did the search hit a previously searched location?
    private boolean m_Stopped = false;
}
