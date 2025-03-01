import java.util.ArrayList;
import java.util.Scanner;
import java.io.File;
import java.io.IOException;

/**
 * Computes the genetic code of the offsprings of different species during mating - I think.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 01/03/25
 */
public class Population
{
    public static void main(String[] args)
    {
        Scanner input = new Scanner(System.in);

        Print("Enter the file name:");
        String filePath = input.nextLine();
        input.close();

        int populationSize = 0;
        int matingCount = 0;
        ArrayList<Critter> critters = new ArrayList<Critter>();
        ArrayList<Pair<Integer, Integer>> matingPairs = new ArrayList<Pair<Integer, Integer>>();

        try (Scanner fileScanner = new Scanner(new File(filePath)))
        {
            populationSize = fileScanner.nextInt(); fileScanner.nextLine(); // Advance scanner cursor past newline
            for (int i = 0; i < populationSize; ++i)
                critters.add(new Critter(fileScanner.nextLine()));

            matingCount = fileScanner.nextInt(); fileScanner.nextLine();    // Advance scanner cursor past newline
            for (int i = 0; i < matingCount; ++i)
            {
                String lineBuf = fileScanner.nextLine();

                int idxSpace = lineBuf.indexOf(" ");
                int idxCritterA = Integer.parseInt(lineBuf.substring(0, idxSpace)) - 1; // Convert number to array index
                int idxCritterB = Integer.parseInt(lineBuf.substring(idxSpace + 1)) - 1;

                matingPairs.add(new Pair<Integer, Integer>(idxCritterA, idxCritterB));
            }
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        Process(critters, matingPairs);
    }

    private static void Process(ArrayList<Critter> critters, final ArrayList<Pair<Integer, Integer>> matingPairs)
    {
        for (final Critter c : critters)
            Print("[%s]", c.GetGeneticCode());

        for (final var pair : matingPairs)
        {
            Critter cA = critters.get(pair.First);
            Critter cB = critters.get(pair.Second);

            Mating mating = new Mating(cA, cB);
            Critter newCritter = mating.Mate();

            Print("[%s]", newCritter.GetGeneticCode());
            critters.add(newCritter);   // New critters must be added to the global population
        }
    }

    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
