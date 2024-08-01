// Adam Foflonker
// FFLADA001
// 31 July 2024
// Unit test for the Seller class/struct

import java.util.Scanner;

public class TestSeller
{
    public static void main(String[] args)
    {
        final Currency RAND = new Currency("R", "ZAR", 100);

        // try-with-resources block used to automatically clean 'scanner' up when it falls out of scope.
        Seller seller = new Seller();
        try (Scanner scanner = new Scanner(System.in))
        {
            System.out.println("Please enter the details of the seller.");

            System.out.print("ID: ");
            seller.ID = scanner.nextLine();

            System.out.print("Name: ");
            seller.Name = scanner.nextLine();

            System.out.print("Location: ");
            seller.Location = scanner.nextLine();

            System.out.print("Product: ");
            seller.Product = scanner.nextLine();

            System.out.print("Price: ");
            seller.unit_price = new Money(scanner.nextLine(), RAND);

            System.out.print("Units: ");
            seller.number_of_units = scanner.nextInt();
        }

        System.out.println("The seller has been successfully created:");
        System.out.printf("ID of the seller: %s\n", seller.ID);
        System.out.printf("Name of the seller: %s\n", seller.Name);
        System.out.printf("Location of the seller: %s\n", seller.Location);
        System.out.printf("The product to sell: %s\n", seller.Product);
        System.out.printf("Product unit price: %s\n", seller.unit_price.toString());
        System.out.printf("The number of available units: %d\n", seller.number_of_units);
    }
}
