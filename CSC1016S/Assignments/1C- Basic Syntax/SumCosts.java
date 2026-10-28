// Adam Foflonker
// FFLADA001
// 26 July 2024
// Summing and printing the result of a series of Rand amounts

import java.util.Scanner;


public class SumCosts
{
    public static void main(String[] args)
    {
        final Currency CURRENCY_ZAR = new Currency("R", "ZAR", 100);
        Money totalMoney = new Money(0, CURRENCY_ZAR);

        // Try-with-resources block to automatically invoke Scanner's destructor and clean it up.
        try (Scanner scanner = new Scanner(System.in))
        {
            while (true)
            {
                System.out.println("Enter an amount or '[D]one' to print the sum and quit:");

                String inAmount = scanner.nextLine();
                if ((inAmount.charAt(0) == 'D') || inAmount.equals("Done"))
                    break;

                totalMoney = totalMoney.add(new Money(inAmount, CURRENCY_ZAR));
            }

            System.out.println("Total: " + totalMoney.toString());
        }
    }
}
