import java.util.Scanner;
import java.util.Map;

/**
 * Program to tell time like a South African.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 20/02/25
 */
public class Converter
{
    /**
     * Converts digital 12-hour time into South African.
     * @param digital the 12-hour-format digital time to convert
     * @return the 12-hour digital time in South African
     */
    public static String DigitalTimeToString(final String digital)
    {
        final String[] HOUR_NAMES = { "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "ten", "eleven", "twelve" };

        // For when minutes are greater than 30
        final Map<Integer, String> MINUTE_DESC_GTT_MAP = Map.of(
                55, "five to",
                50, "ten to",
                45, "quarter to",
                40, "twenty to",
                35, "twenty-five to"
        );

        // For when minutes are less than 30
        final Map<Integer, String> MINUTE_DESC_LTT_MAP = Map.of(
                5, "five past",
                10, "ten past",
                15, "quarter past",
                20, "twenty past",
                25, "twenty-five past",
                30, "half past"
        );

        int colonIdx = digital.indexOf(':');
        int hour = Integer.parseInt(digital.substring(0, colonIdx));
        int minutes = Integer.parseInt(digital.substring(colonIdx + 1));
        int minutesRounded = Math.round(minutes / 5.0f) * 5;

        String res = "";
        if (minutes <= 2)
            res = HOUR_NAMES[hour - 1] + " o'clock";
        else if (minutes <= 32)
            res = MINUTE_DESC_LTT_MAP.get(minutesRounded) + " " + HOUR_NAMES[hour - 1];
        else
            res = MINUTE_DESC_GTT_MAP.get(minutesRounded) + " " + HOUR_NAMES[hour % 12];

        return (minutes % 5 == 0) ? res : "about " + res;
    }

    public static void main(String[] args)
    {
        Scanner input = new Scanner(System.in);

        while (true)
        {
            Print("Enter a time or 'quit':");

            String time = input.nextLine();
            if (time.equals("quit"))
                break;

            Print(DigitalTimeToString(time));
        }

        Print("Done");
        input.close();
    }

    private static void Print(final String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
