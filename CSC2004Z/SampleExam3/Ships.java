import java.util.ArrayList;
import java.util.Scanner;
import java.io.File;
import java.io.IOException;

/**
 * Calculates the intersection of the travel-paths of 2 ships and checks which ship is closest.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 01/03/25
 */
public class Ships
{
    public static void main(String[] args)
    {
        Print("Enter the name of the ship data file:");

        Scanner input = new Scanner(System.in);
        String filePath = input.nextLine();
        input.close();

        ArrayList<Pair<Line, Line>> linePairs = new ArrayList<Pair<Line, Line>>();
        try (Scanner fileScanner = new Scanner(new File(filePath)))
        {
            while (fileScanner.hasNextLine())
            {
                Line line1 = new Line(fileScanner.nextLine());
                Line line2 = new Line(fileScanner.nextLine());
                linePairs.add(new Pair<Line, Line>(line1, line2));
            }
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        Process(linePairs);
        Print("Done");
    }

    private static void Process(final ArrayList<Pair<Line, Line>> linePairs)
    {
        int i = 1;
        for (final var pair : linePairs)
        {
            final Line l1 = pair.First;
            final Line l2 = pair.Second;

            double xI = ((l1.b * l2.c) - (l2.b * l1.c)) / ((l1.a * l2.b) - (l2.a * l1.b));
            double yI = ((l2.a * l1.c) - (l1.a * l2.c)) / ((l1.a * l2.b) - (l2.a * l1.b));

            double dS1 = Math.sqrt(Math.pow(l1.x - xI, 2) + Math.pow(l1.y - yI, 2));
            double dS2 = Math.sqrt(Math.pow(l2.x - xI, 2) + Math.pow(l2.y - yI, 2));

            String nearestStr = "";
            if ((int)Math.round(dS1) == (int)Math.round(dS2)) // Round to avoid precision issues when checking equality
                nearestStr = "Tied";
            else
                nearestStr = (dS1 > dS2) ? "Ship S2 is nearest" : "Ship S1 is nearest";

            Print("Pair %d: Intersection point: (%.1f, %.1f); Ship S1's distance is %.1f; Ship S2's distance is %.1f; %s.",
                i++, xI, yI, dS1, dS2, nearestStr);
        }
    }

    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
