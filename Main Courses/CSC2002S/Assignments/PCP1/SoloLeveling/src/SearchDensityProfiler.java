import java.io.ByteArrayOutputStream;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.PrintStream;
import SoloLeveling.Serial.DungeonHunter;
import SoloLeveling.Parallel.DungeonHunterParallel;

/**
 * Measures the optimal search density (num searches) for both the serial and parallel implementations of the
 * SoloLeveling program, using a gate size of 200 and a random seed of 627
 *
 * @see SoloLeveling.Serial.DungeonHunter
 * @see SoloLeveling.Parallel.DungeonHunterParallel
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 15/08/2025
 */
public class SearchDensityProfiler
{
    /** Where to output the profiling data */
    public static final String OUTPUT_FILE_PATH = "SearchDensityTestOutputData.csv";

    /** Number of warm-up iterations per test case */
    public static final int WARMUP_ITERATIONS = 3;

    /** Number of timed iterations per test case */
    public static final int MEASURE_ITERATIONS = 5;

    /** The fixed gate size for search density tests */
    public static final int GATE_SIZE = 200;

    /** The fixed random seed for search density tests */
    public static final int RANDOM_SEED = 627;

    /** The array of search densities to measure */
    public static final double[] SEARCH_DENSITIES =
    {
        0.05,
        0.1,
        0.15,
        0.2,
        0.25,
        0.3,
        0.35,
        0.4,
        0.45,
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
        1.0
    };

    /**
     * Entry-point for {@link SearchDensityProfiler}.
     *
     * @param args command-line arguments
     */
    public static void main(String[] args)
    {
        try (PrintWriter writer = new PrintWriter(new FileWriter(OUTPUT_FILE_PATH)))
        {
            writer.println("GateSize,SearchDensity,SerialTimeMS,ParallelTimeMS");

            // Warm-up phase
            for (int i = 0; i < WARMUP_ITERATIONS; ++i)
                RunTest(i, null); // Pass a null writer to ignore these timings

            for (int i = 0; i < SEARCH_DENSITIES.length; ++i)
            {
                for (int j = 0; j < MEASURE_ITERATIONS; ++j)
                    RunTest(i, writer);
            }
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }

        Print("Done!");
        Print("Output saved to \"%s\".", OUTPUT_FILE_PATH);
    }

    // Runs an individual profile test, serial first, then parallel
    private static void RunTest(int densityIndex, PrintWriter outputFileWriter)
    {
        final String TOKEN_MS = " ms";

        double searchDensity = SEARCH_DENSITIES[densityIndex];
        String[] cmdArgs =
        {
            Integer.toString(GATE_SIZE),
            Double.toString(searchDensity),
            Integer.toString(RANDOM_SEED)
        };

        Print("Running test with density: %.2f...", searchDensity);

        // Preserve the original System.out stream so we can capture the outputs from the profiled programs
        PrintStream originalSysOut = System.out;
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream(byteArrayOutputStream);
        System.setOut(ps);

        DungeonHunter.main(cmdArgs);
        DungeonHunterParallel.main(cmdArgs);

        System.out.flush();
        System.setOut(originalSysOut);

        String output = byteArrayOutputStream.toString();
        String serialTime = GetTimeFromOutput(output, 1);
        String parallelTime = GetTimeFromOutput(output, 2);
        Print("Serial time: %s\nParallel time: %s\n", serialTime, parallelTime);

        if (outputFileWriter != null)
        {
            serialTime = serialTime.substring(0, serialTime.indexOf(TOKEN_MS));
            parallelTime = parallelTime.substring(0, parallelTime.indexOf(TOKEN_MS));
            outputFileWriter.write(String.format("%d,%.2f,%s,%s\n", GATE_SIZE, searchDensity, serialTime, parallelTime));

            // Flush each time to force the write to happen NOW, rather then only at the end
            outputFileWriter.flush();
        }

        // Request the Garbage Collector to run at the end of each test to ensure everything has been cleaned up
        System.gc();
    }

    // Extracts the time from program output
    private static String GetTimeFromOutput(final String outputStr, int n)
    {
        final String TOKEN_TIME = "time";
        final int TOKEN_TIME_LENGTH = TOKEN_TIME.length();

        int start = 0;
        int idxToken = -1;

        for (int i = 0; i < n; ++i)
        {
            idxToken = outputStr.indexOf(TOKEN_TIME, start);
            if (idxToken == -1)
                return null;

            start = idxToken + TOKEN_TIME_LENGTH;
        }

        int idxEol = outputStr.indexOf("\n", idxToken);
        if (idxEol == -1)
            idxEol = outputStr.length();

        return outputStr.substring(idxToken + TOKEN_TIME_LENGTH + 2, idxEol);
    }

    // Print line helper
    private static void Print(final String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
