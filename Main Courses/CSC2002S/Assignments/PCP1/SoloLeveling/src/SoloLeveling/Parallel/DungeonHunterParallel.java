package SoloLeveling.Parallel;

import java.util.Random;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;

/**
 * Parallel implementation of the {@link SoloLeveling.Serial.DungeonHunter} program.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 15/08/2025
 */
public class DungeonHunterParallel
{
    /**
     * The return-value for {@link ComputeHuntMaxTask}.
     * This class is meant to act like a C-style struct allowing us to return "multiple values"
     */
    static class ComputeMaxHuntResult
    {
        /**
         * Creates a new {@link ComputeMaxHuntResult}.
         *
         * @param value the value of this result (max)
         * @param index the index of the value (finder)
         */
        public ComputeMaxHuntResult(int value, int index)
        {
            Value = value;
            Index = index;
        }

        /** The value of this result */
        public int Value;

        /** The index at which {@code Value} was found */
        public int Index;
    }

    /** Recursive parallelized implementation for finding the max {@link HuntParallel} value */
    static class ComputeHuntMaxTask extends RecursiveTask<ComputeMaxHuntResult>
    {
        /**
         * Creates a new {@link ComputeHuntMaxTask}.
         *
         * @param searches the array of {@link HuntParallel} to find the max of
         * @param start the starting index
         * @param end the ending index
         */
        public ComputeHuntMaxTask(final HuntParallel[] searches, int start, int end)
        {
            m_Searches = searches;
            m_Start = start;
            m_End = end;
        }

        /** Recursively computes the max hunt value */
        @Override
        protected ComputeMaxHuntResult compute()
        {
            int length = m_End - m_Start;
            if (length == 1)
            {
                m_Searches[m_Start].fork();
                return new ComputeMaxHuntResult(m_Searches[m_Start].join(), m_Start);
            }

            // Recursively split task into two halves
            int mid = m_Start + (m_End - m_Start) / 2;
            ComputeHuntMaxTask leftTask = new ComputeHuntMaxTask(m_Searches, m_Start, mid);
            ComputeHuntMaxTask rightTask = new ComputeHuntMaxTask(m_Searches, mid, m_End);

            leftTask.fork();
            ComputeMaxHuntResult rightResult = rightTask.compute();
            ComputeMaxHuntResult leftResult = leftTask.join();

            return (leftResult.Value >= rightResult.Value) ? leftResult : rightResult; // Return the max
        }

        // Search array
        private final HuntParallel[] m_Searches;

        // Search starting index
        private final int m_Start;

        // Search ending index
        private final int m_End;
    }

    /**
     * The entry-point for {@link DungeonHunterParallel}.
     *
     * @param args command-line arguments
     */
    public static void main(String[] args)
    {
        double xMin, xMax, yMin, yMax;

        int numSearches = 10;
        int gateSize = 10;

        int randomSeed = 0;
        Random rand = new Random();


        if (args.length != 3)
        {
            System.out.println("Incorrect number of command line arguments provided.");
            System.exit(0);
        }

        try
        {
            gateSize = Integer.parseInt(args[0]);
            if (gateSize <= 0)
                throw new IllegalArgumentException("Grid size must be greater than 0.");

            numSearches = (int)(Double.parseDouble(args[1]) * (gateSize * 2) * (gateSize * 2) * DungeonMapParallel.RESOLUTION);

            randomSeed = Integer.parseInt(args[2]);
            if (randomSeed < 0)
                throw new IllegalArgumentException("Random seed must be non-negative.");
            else if (randomSeed > 0)
                rand = new Random(randomSeed);
        }
        catch (NumberFormatException e)
        {
            System.err.println("Error: All arguments must be numeric.");
            System.exit(1);
        }
        catch (IllegalArgumentException e)
        {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }

        xMin = -gateSize;
        xMax = gateSize;
        yMin = -gateSize;
        yMax = gateSize;

        HuntParallel[] searches = new HuntParallel[numSearches];
        DungeonMapParallel dungeon = new DungeonMapParallel(xMin, xMax, yMin, yMax, randomSeed);

        int dungeonRows = dungeon.GetRows();
        int dungeonColumns = dungeon.GetColumns();

        // ForkJoinPool.close() doesn't exist on Nightmare's version of the OpenJDK.
        // This attribute is to suppress resource leak warnings on newer versions of
        // the OpenJDK contaning ForkJoinPool.close()
        @SuppressWarnings("resource")
        ForkJoinPool pool = new ForkJoinPool();

        // Begin timer
        Tick();

        for (int i = 0; i < numSearches; ++i)
            searches[i] = new HuntParallel(i + 1, rand.nextInt(dungeonRows), rand.nextInt(dungeonColumns), dungeon);

        ComputeMaxHuntResult result = pool.invoke(new ComputeHuntMaxTask(searches, 0, numSearches));
        pool.shutdown();

        int max = result.Value;
        int finder = result.Index;

        // End timer
        Tock();

        System.out.printf("\t dungeon size: %d,\n", gateSize);
        System.out.printf("\t rows: %d, columns: %d\n", dungeonRows, dungeonColumns);
        System.out.printf("\t x: [%f, %f], y: [%f, %f]\n", xMin, xMax, yMin, yMax );
        System.out.printf("\t Number searches: %d\n", numSearches );

        // Total computation time
        System.out.printf("\n\t time: %d ms\n", s_EndTime - s_StartTime);
        int tmp = dungeon.GetGridPointsEvaluated();
        System.out.printf("\tnumber dungeon grid points evaluated: %d  (%2.0f%s)\n", tmp,
            (tmp * 1.0 / (dungeonRows * dungeonColumns * 1.0 )) * 100.0, "%");

        // Results
        System.out.printf("Dungeon Master (mana %d) found at:  ", max);
        System.out.printf("x=%.1f y=%.1f\n\n", dungeon.GetXcoord(searches[finder].GetRowPos()),
            dungeon.GetYcoord(searches[finder].GetColPos()));

        dungeon.VisualisePowerMap("visualiseSearch.png", false);
        dungeon.VisualisePowerMap("visualiseSearchPath.png", true);
    }

    /** Not currently being used */
    public static final boolean DEBUG = false;

    // Record current system time as the start time
    private static void Tick() { s_StartTime = System.currentTimeMillis(); }

    // Record current system time as the end time
    private static void Tock() { s_EndTime = System.currentTimeMillis(); }

    // The start time of the max hunt value search
    private static long s_StartTime = 0;

    // The end time of the max hunt value search
    private static long s_EndTime = 0;
}
