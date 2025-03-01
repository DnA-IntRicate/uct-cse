/**
 * Represents a 24-hour-format time for use in {@link Bookings}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 28/02/25
 */
public class Time
{
    /**
     * Constructs a new 24-hour format {@link Time} from 12-hour format.
     *
     * @param timeStr12Hour the 12-hour format time string used to initialize this {@link Time}
     */
    public Time(String timeStr12Hour)
    {
        int idxColon = timeStr12Hour.indexOf(":");
        int idxSpace = timeStr12Hour.indexOf(" ");

        m_Hours = Integer.parseInt(timeStr12Hour.substring(0, idxColon));
        m_Minutes = Integer.parseInt(timeStr12Hour.substring(idxColon + 1, idxSpace));
        String meridiem  = timeStr12Hour.substring(idxSpace + 1); // Meridiem indicator is found after the first space

        // Convert to 24-hour format
        if (meridiem.equals("pm"))
            m_Hours += (m_Hours == 12) ? 0 : 12;
        else if (m_Hours == 12)  // else Meridiem is "am" here
            m_Hours = 0;
    }

    public int GetHours() { return m_Hours; }
    public int GetMinutes() { return m_Minutes; }

    /**
     * Returns this {@link Time} as minutes elapsed since 00:00 (12 AM) to make comparisons easier
     *
     * @return this time as minutes elapsed since 00:00 (12 AM)
     */
    public int GetTimeMinutes() { return (m_Hours * 60) + m_Minutes; }

    @Override
    public boolean equals(Object other)
    {
        if (!(other instanceof Time))
            return false;

        Time myOther = (Time)other;
        return (m_Hours == myOther.m_Hours) && (m_Minutes == myOther.m_Minutes);
    }

    private int m_Hours;
    private int m_Minutes;
}
