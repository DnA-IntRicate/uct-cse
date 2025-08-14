package SoloLeveling.Parallel;

// imports
import java.util.Random;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;

// import SoloLeveling.DungeonMap;

/**
 * Parallel implementation of the {@link SoloLeveling.DungeonHunter} program.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 11/08/2025
 */
public class DungeonHunterParallel
{
    static class ComputeMaxHuntResult
    {
        ComputeMaxHuntResult(int value, int index)
        {
            Value = value;
            Index = index;
        }

        public int Value;
        public int Index;
    }

    static class ComputeHuntMaxTask extends RecursiveTask<ComputeMaxHuntResult>
    {
        ComputeHuntMaxTask(final HuntParallel[] searches, int start, int end)
        {
            m_Searches = searches;
            m_Start = start;
            m_End = end;
        }

        @Override
        protected ComputeMaxHuntResult compute()
        {
            int length = m_End - m_Start;
            if (length == 1)
            {
                m_Searches[m_Start].fork();
                return new ComputeMaxHuntResult(m_Searches[m_Start].join(), m_Start);
            }

            // Split task into two halves
            int mid = m_Start + (m_End - m_Start) / 2;
            ComputeHuntMaxTask leftTask = new ComputeHuntMaxTask(m_Searches, m_Start, mid);
            ComputeHuntMaxTask rightTask = new ComputeHuntMaxTask(m_Searches, mid, m_End);

            leftTask.fork();
            ComputeMaxHuntResult rightResult = rightTask.compute();
            ComputeMaxHuntResult leftResult = leftTask.join();

            return (leftResult.Value >= rightResult.Value) ? leftResult : rightResult; // Return max
        }

        private final HuntParallel[] m_Searches;
        private final int m_Start;
        private final int m_End;
    }

    public static void main(String[] args)
    {
        double xMin, xMax, yMin, yMax; // Dungeon limits - dungeons are square

        int numSearches = 10;
        int gateSize = 10;

        Random rand = new Random();
        int randomSeed = 0;

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

            numSearches = (int)(Double.parseDouble(args[1]) * (gateSize * 2) * (gateSize * 2) *
                DungeonMapParallel.RESOLUTION);

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

        DungeonMapParallel dungeon = new DungeonMapParallel(xMin, xMax, yMin, yMax, randomSeed);

        int dungeonRows = dungeon.GetRows();
        int dungeonColumns = dungeon.GetColumns();
        HuntParallel[] searches = new HuntParallel[numSearches];

        ForkJoinPool pool = new ForkJoinPool();

        Tick(); // Begin timer
        for (int i = 0; i < numSearches; ++i)  // Initialize searches at random locations in dungeon
            searches[i] = new HuntParallel(i + 1, rand.nextInt(dungeonRows), rand.nextInt(dungeonColumns), dungeon);

        ComputeMaxHuntResult result = pool.invoke(new ComputeHuntMaxTask(searches, 0, numSearches));
        pool.shutdown();
        pool.close();

        int max = result.Value;
        int finder = result.Index;

        Tock(); // End timer

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

    // TODO: Comment
    private static void Tick() { s_StartTime = System.currentTimeMillis(); }

    // TODO: Comment
    private static void Tock(){ s_EndTime=System.currentTimeMillis(); }

    // TODO: Why?
    public static final boolean DEBUG = false;

    // TODO: Comment
    private static long s_StartTime = 0;

    // TODO: Comment
    private static long s_EndTime = 0;
}
