/**********************************************************************************
* MIT License
*
* Copyright (c) 2024 Adam Foflonker
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all
* copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
***********************************************************************************/

import java.util.Scanner;

/**
 * Java implementation of CSC1015F-2024 Assignment 5, Question 2.
 *
 * @author Adam Foflonker
 * @version 08/20/24
 */
public class Convert
{
    /**
     * Returns the name of the month of the year specified by {@code month}.
     *
     * @param month the month of the year [1 .. 12].
     * @return The name of the month.
     */
    public static String MonthName(final int month)
    {
        final String[] MONTHS =
        {
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        };

        return MONTHS[month - 1];
    }

    /**
     * Returns a formatted day-of-month number with the correct suffix.
     *
     * @param day the day to format.
     * @return The formatted day.
     */
    public static String FormatDay(final int day)
    {
        if ((day >= 11) && (day <= 13))
            return Integer.toString(day) + "th";

        switch (day % 10)   // Get the units digit of the day
        {
            case 1: return Integer.toString(day) + "st";
            case 2: return Integer.toString(day) + "nd";
            case 3: return Integer.toString(day) + "rd";
        }

        return Integer.toString(day) + "th";
    }

    /**
     * Returns a formatted time with the correct meridiem suffix.
     *
     * @param time the time to format.
     * @return The formatted time.
     */
    public static String FormatTime(final String time)
    {
        final int colonPos = time.indexOf(':');
        final int minutes = Integer.parseInt(time.substring(colonPos + 1));

        int hours = Integer.parseInt(time.substring(0, colonPos));
        final String meridiem = (hours >= 12) ? "pm" : "am";

        if (hours > 12)
            hours = hours % 12;

        return String.format("%02d:%d %s", hours, minutes, meridiem);
    }

    /**
     * Returns {@code year} in the format: 'yy.
     *
     * @param year the year to format.
     * @return The formatted year.
     */
    public static String FormatYear(final int year)
    {
        return '\'' + Integer.toString(year).substring(2);
    }

    /**
     * Sample Input and Output:
     *
     * <pre>
     * Input:
     * Case 1: "2021-04-09 04:33"
     * Case 2: "2000-11-23 23:15"
     *
     * Output:
     * Case 1: "4:33 am on the 9th of April '21"
     * Case 2: "11:15 pm on the 23rd of November '00"
     * </pre>
     */
    public static void main(String[] args)
    {
        System.out.println("Enter the date and time (yyyy-mm-dd hh:mm):");

        String inDateTime;
        try (Scanner scanner = new Scanner(System.in)) { inDateTime = scanner.nextLine(); }

        int day, month, year;
        try (Scanner dateScanner = new Scanner(inDateTime.substring(0, inDateTime.indexOf(' '))))
        {
            dateScanner.useDelimiter("-");
            year = dateScanner.nextInt();
            month = dateScanner.nextInt();
            day = dateScanner.nextInt();
        }

        final String time = FormatTime(inDateTime.substring(inDateTime.indexOf(' ')).trim());
        final String dayStr = FormatDay(day);
        final String monthStr = MonthName(month);
        final String yearStr = FormatYear(year);

        System.out.printf("%s on the %s of %s %s", time, dayStr, monthStr, yearStr);
    }
}
