import java.util.Scanner;
import java.util.ArrayList;

/**
 * Manages bookings for stuff.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 28/02/25
 */
public class Bookings
{
    public static void main(String[] args)
    {
        Scanner input = new Scanner(System.in);

        Print("Enter the number of bookings:");
        int numBookings = input.nextInt(); input.nextLine();    // Advance scanner cursor past newline

        Print("Enter the bookings, one per line:");

        ArrayList<BookingRequest> bookings = new ArrayList<BookingRequest>();
        for (int i = 0; i < numBookings; ++i)
        {
            String bookingStr = input.nextLine();
            bookings.add(new BookingRequest(bookingStr));
        }

        input.close();
        Print(Process(bookings));
    }

    private static String Process(final ArrayList<BookingRequest> bookings)
    {
        if (bookings.isEmpty() || (bookings.size() == 1))
            return "Good to go!";

        int overlapping = 0;
        for (int i = 0; i < bookings.size(); ++i)
        {
            for (int j = i + 1; j < bookings.size(); ++j)   // brute-force pairwise comparison
            {
                if (bookings.get(i).IsOverlapping(bookings.get(j)))
                    overlapping++;
            }
        }

        if (overlapping == 0)
            return "Good to go!";

        return String.format("Let's play Sardines! Number of pairs that clash: %d.", overlapping);
    }

    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
