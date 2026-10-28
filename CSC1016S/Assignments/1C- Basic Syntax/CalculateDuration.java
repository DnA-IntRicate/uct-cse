// Adam Foflonker
// FFLADA001
// 26 July 2024
// Calculating the time period between 2 time-points.

import java.util.Scanner;


public class CalculateDuration
{
    public static void main(String[] args)
    {
        Time timeA;
        Time timeB;

        // Try-with-resources block to automatically invoke Scanner's destructor and clean it up.
        try (Scanner scanner = new Scanner(System.in);)
        {
            System.out.println("Enter time A:");
            timeA = new Time(scanner.nextLine());

            System.out.println("Enter time B:");
            timeB = new Time(scanner.nextLine());
        }

        System.out.printf("The time %s occurs %d minutes after the time %s.", timeB.toString(),
        timeB.subtract(timeA).intValue("minute"), timeA.toString());
    }
}
