import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;

/**
 * Computes the best way to optimize probing in an {@link LPHashTable}.
 *
 * @see HashTable
 * @see LPHashTable
 * @see QPHashTable
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 12/04/25
 */
public class Optimize
{
    public static void main(String[] args)
    {
        ArrayList<String> data = new ArrayList<String>();
        try (Scanner fileScanner = new Scanner(new File("mydata.txt")))
        {
            while (fileScanner.hasNextLine())
                data.add(fileScanner.nextLine());
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        int minProbeCount = -1;
        int weightCombinations = 1;
        int totalPermutations = (int)Math.pow(5, 9); // 5^9 possible permutations

        for (int i = 0; i < totalPermutations; ++i)
        {
            int[] weights = new int[9];
            int num = i;

            for (int j = 8; j >= 0; --j)    // Compute every possible permutation of weights
            {
                weights[j] = num % 5; // 0 .. 4
                num /= 5;
            }

            HashTable table = new LPHashTable(37);
            table.setWeights(weights);

            for (final String key : data)
                table.insert(key);

            int probeCount = table.getProbeCount();
            if ((minProbeCount == -1) || (probeCount < minProbeCount))
            {
                minProbeCount = probeCount;
                weightCombinations = 1;
            }
            else if (probeCount == minProbeCount)
                weightCombinations++;
        }

        String out = String.format("%d %d", minProbeCount, weightCombinations);
        System.out.println(out);

        // Write results file
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("results.txt")))
        {
            writer.write(out);
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
    }
}
