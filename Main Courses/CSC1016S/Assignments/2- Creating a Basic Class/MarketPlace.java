import java.io.File;
import java.io.FileNotFoundException;
//
import java.util.Scanner;
/**
 * See Assignment II Question II
 *
 * @author Stephan Jamieson
 * @version 26/7/2019
 *
 * Answered by:
 * Adam Foflonker
 * FFLADA001
 * 1 August 2024
 */
public class MarketPlace {

    private MarketPlace() {}

    private final static Currency RAND = new Currency("R", "ZAR", 100);


    // Create an instance of Seller with attributes ID, name, location, product,
    // unit_price and number_of_units
    private static Seller makeSeller(final String data) {
        final Scanner scanner = new Scanner(data.trim());
        scanner.useDelimiter("\\s*,\\s*");

        // Add your code here
        Seller seller = new Seller();
        seller.ID = scanner.next();
        seller.Name = scanner.next();
        seller.Location = scanner.next();
        seller.Product = scanner.next();
        seller.unit_price = new Money(scanner.next(), RAND);
        seller.number_of_units = scanner.nextInt();
        scanner.close();

        return seller;
    }

    // Read the contents of CSV file into an array.
    // See the Appendix on page 4 of the Assignment sheet.
    private static Seller[] parseFile(final String fileName) throws FileNotFoundException {
        final Scanner inFile = new Scanner(new File(fileName));
        Seller[] sellers = null;

        if (inFile.hasNextLine()) {
            sellers = new Seller[Integer.parseInt(inFile.nextLine().trim())];
            for (int index=0; index<sellers.length; index++) {
                sellers[index] = makeSeller(inFile.nextLine());
            }
        }
        inFile.close();
        return sellers;
    }

    public static void main(final String[] args) throws FileNotFoundException {
        final Scanner inKey = new Scanner(System.in);
        System.out.println("Enter the name of a \"Comma Separated Values\" (CSV) file:");
        final Seller[] sellers = parseFile(inKey.nextLine());

        // Your Code here
        if ((sellers == null) || (sellers.length == 0))
        {
            System.out.println("The file contains no seller data.");
            inKey.close();

            return;
        }

        System.out.println("Enter the name of a product:");
        String productName = inKey.nextLine();

        System.out.println("Enter the number of units required:");
        int numUnitsRequired = Integer.parseInt(inKey.nextLine());

        System.out.println("Enter the maximum unit price:");
        Money maxPrice = new Money(inKey.nextLine(), RAND);

        boolean anyProductFound = false;
        for (final Seller seller : sellers)
        {
            if (!seller.Product.equals(productName))
                continue;

            if (seller.number_of_units < numUnitsRequired)
                continue;

            if (seller.unit_price.compareTo(maxPrice) > 0)
                continue;

            System.out.printf("%s : %s in %s has %d %s for %s each.\n", seller.ID, seller.Name, seller.Location,
            seller.number_of_units, seller.Product, seller.unit_price.toString());

            if (!anyProductFound)
                anyProductFound = true;
        }

        if (!anyProductFound)
            System.out.println("None found.");

        inKey.close();
    }
}
