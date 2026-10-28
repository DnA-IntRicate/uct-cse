import java.util.Scanner;
import java.util.Map;
import java.io.File;
import java.io.IOException;

/**
 * Checks if whether a list of dates are oddities or not (contains all odd digits). If a date is not an oddity, the nearest
 * date that is an oddity is computed.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 22/02/25
 */
public class Oddities
{
    public static void main(String[] args)
    {
        Print("Enter the name of the text file of dates:");

        Scanner input = new Scanner(System.in);
        String filePath = input.nextLine();
        input.close();

        try (Scanner fileScanner = new Scanner(new File(filePath)))
        {
            while (fileScanner.hasNextLine())
            {
                String lineBuf = fileScanner.nextLine();
                try (Scanner dateScanner = new Scanner(lineBuf))
                {
                    dateScanner.useDelimiter("/");
                    int day = dateScanner.nextInt();
                    int month = dateScanner.nextInt();
                    int year = dateScanner.nextInt();

                    Print(ProcessDate(day, month, year));
                }
            }
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        Print("Done");
    }

    /** Checks whether the given date is an oddity or not. If not, returns the nearest date that is an oddity. */
    private static String ProcessDate(int day, int month, int year)
    {
        if (IsDateOddity(day, month, year))
            return String.format("The date %d/%d/%d has all odd digits.", day, month, year);

        int myDay = day;
        int myMonth = month;
        int myYear = year;
        int daysLater = 0;

        while (!IsDateOddity(myDay, myMonth, myYear))
        {
            if (myDay < DaysInMonth(myMonth, myYear))
                myDay++;
            else
            {
                myDay = 1;
                myMonth++;

                if (myMonth > 12)
                {
                    myMonth = 1;
                    myYear++;
                }
            }

            daysLater++;
        }

        return String.format("The first date after %d/%d/%d with all odd digits is %d/%d/%d which is %d day%s later.",
            day, month, year, myDay, myMonth, myYear, daysLater, (daysLater == 1) ? "" : "s");
    }

    /** Checks if all the digits in the given int are odd numbers. */
    private static boolean IsOddity(int x)
    {
        while (x > 0)
        {
            int lastDigit = x % 10;
            if (lastDigit % 2 == 0)
                return false;

            x /= 10;
        }

        return true;
    }

    private static boolean IsDateOddity(int day, int month, int year)
    {
        return IsOddity(day) && IsOddity(month) && IsOddity(year);
    }

    private static int DaysInMonth(int month, int year)
    {
        if (month == 2) // February
            return IsLeapYear(year) ? 29 : 28;

        final Map<Integer, Integer> MONTH_DAYS_MAP = Map.ofEntries(
            Map.entry(1, 31),  // January
            Map.entry(3, 31),  // March
            Map.entry(4, 30),  // April
            Map.entry(5, 31),  // May
            Map.entry(6, 30),  // June
            Map.entry(7, 31),  // July
            Map.entry(8, 31),  // August
            Map.entry(9, 30),  // September
            Map.entry(10, 31), // October
            Map.entry(11, 30), // November
            Map.entry(12, 31)  // December
        );

        return MONTH_DAYS_MAP.get(month);
    }

    private static boolean IsLeapYear(int year)
    {
        if (year % 400 == 0)
            return true;

        if ((year % 4 == 0) && (year % 100 != 0))
            return true;

        return false;
    }

    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
