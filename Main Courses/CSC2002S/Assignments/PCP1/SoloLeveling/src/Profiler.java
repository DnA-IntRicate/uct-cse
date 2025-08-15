import java.io.ByteArrayOutputStream;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.PrintStream;
import SoloLeveling.Serial.DungeonHunter;
import SoloLeveling.Parallel.DungeonHunterParallel;

/**
 * Speedup profiler for the parallel vs serial implementations of the SoloLeveling program.
 *
 * @see SoloLeveling.Serial.DungeonHunter
 * @see SoloLeveling.Parallel.DungeonHunterParallel
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 15/08/2025
 */
public class Profiler
{
    /** Where to output the profiling data */
    public static final String OUTPUT_FILE_PATH = "TestOutputData.csv";

    /** Number of warm-up iterations per test case */
    public static final int WARMUP_ITERATIONS = 3;

    /** Number of timed iterations per test case */
    public static final int MEASURE_ITERATIONS = 10;

    /** The optimal search density for profiling on my 4-Core AMD Ryzen 3 7320U */
    public static final double SEARCH_DENSITY = 0.35;

    /** The random seed to use for profiling */
    public static final int RANDOM_SEED = 627;

    /** The maximum gate size for profiling */
    public static final int MAX_GATE_SIZE = 200;

    /** The minimum gate size for profiling */
    public static final int MIN_GATE_SIZE = 20;

    /** The increment step for each gate size */
    public static final int GATE_SIZE_STEP = 10;

    /**
     * Entry-point for {@link Profiler}.
     *
     * @param args command-line arguments
     */
    public static void main(String[] args)
    {
        try (PrintWriter writer = new PrintWriter(new FileWriter(OUTPUT_FILE_PATH)))
        {
            writer.println("GateSize,SerialTimeMS,ParallelTimeMS");

            // Warm-up phase here...
            for (int i = 0; i < WARMUP_ITERATIONS; ++i)
                RunTest(i, MIN_GATE_SIZE, SEARCH_DENSITY, null); // Pass a null writer to ignore these timings

            for (int gateSize = MIN_GATE_SIZE; gateSize < MAX_GATE_SIZE; gateSize += GATE_SIZE_STEP)
            {
                for (int i = 0; i < MEASURE_ITERATIONS; ++i)
                    RunTest(i, gateSize, SEARCH_DENSITY, writer);
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
    private static void RunTest(int testIndex, int gateSize, double searchDensity, PrintWriter outputFileWriter)
    {
        final String TOKEN_MS = " ms";

        String[] cmdArgs =
        {
            Integer.toString(gateSize),
            Double.toString(searchDensity),
            Integer.toString(RANDOM_SEED)
        };

        Print("Running test #%d with GateSize: %d...", testIndex + 1, gateSize);

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
            outputFileWriter.write(String.format("%d,%s,%s\n", gateSize, serialTime, parallelTime));

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
