/**
 * Stores the start and finish times of work shifts for use in the {@link Employee} class.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 11/09/24
 */
public class Shift
{
    /**
     * Creates a new {@link Shift} representing a shift worked between the given date-times.
     *
     * @param start the shift-start
     * @param finish the shift-end
     */
    public Shift(CalendarTime start, CalendarTime finish)
    {
        m_Start = start;
        m_Finish = finish;
    }

    /**
     * Checks if this shift occurs within the given {@link Week}.
     *
     * @param w the {@link Week} to check
     * @return {@code true} if this shift occurs within {@code w}, {@code false} othwerise
     */
    public boolean inWeek(Week w)
    {
        return w.includes(m_Start.date()) && w.includes(m_Finish.date());
    }

    /**
     * Checks if this shift is inclusive of the given {@link Date}.
     *
     * @param d the {@link Date} to check
     * @return {@code true} if this shift is inclusive of {@code d}, {@code false} othwerise
     */
    public boolean includesDate(Date d)
    {
        return (m_Start.date().compareTo(d) <= 0) && (m_Finish.date().compareTo(d) >= 0);
    }

    /**
     * Returns the length of this shift.
     *
     * @return the length of this shift as a {@link Duration}
     */
    public Duration length()
    {
        return m_Finish.subtract(m_Start);
    }

    /**
     * Get the start {@link CalendarTime} for this shift.
     *
     * @return the start of this shift
     */
    public CalendarTime start() { return m_Start; }

    /**
     * Get the end {@link CalendarTime} for this shift.
     *
     * @return the end of this shift
     */
    public CalendarTime finish() { return m_Finish; }

    /**
     * Returns a string representation of this shift.
     *
     * @return a string in the format: of the form {@code "<date>%<time> - <date>%<time>"}
     */
    public String toString()
    {
        return String.format("%s%%%s - %s%%%s", m_Start.date().toString(), m_Start.time().toString(),
        m_Finish.date().toString(), m_Finish.time().toString());
    }

    /** The start date-time of this shift. */
    private CalendarTime m_Start;

    /** The end date-time of this shift. */
    private CalendarTime m_Finish;
}
