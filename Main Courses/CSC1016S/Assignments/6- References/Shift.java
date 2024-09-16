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
        s_Start = start;
        s_Finish = finish;
    }

    /**
     * Checks if this shift occurs within the given {@link Week}.
     *
     * @param w the {@link Week} to check
     * @return {@code true} if this shift occurs within {@code w}, {@code false} othwerise
     */
    public boolean inWeek(Week w)
    {
        return w.includes(s_Start.date()) && w.includes(s_Finish.date());
    }

    /**
     * Checks if this shift is inclusive of the given {@link Date}.
     *
     * @param d the {@link Date} to check
     * @return {@code true} if this shift is inclusive of {@code d}, {@code false} othwerise
     */
    public boolean includesDate(Date d)
    {
        return (s_Start.date().compareTo(d) <= 0) && (s_Finish.date().compareTo(d) >= 0);
    }

    /**
     * Returns the length of this shift.
     *
     * @return the length of this shift as a {@link Duration}
     */
    public Duration length()
    {
        return s_Finish.subtract(s_Start);
    }

    /**
     * Get the start {@link CalendarTime} for this shift.
     *
     * @return the start of this shift
     */
    public CalendarTime start() { return s_Start; }

    /**
     * Get the end {@link CalendarTime} for this shift.
     *
     * @return the end of this shift
     */
    public CalendarTime finish() { return s_Finish; }

    /**
     * Returns a string representation of this shift.
     *
     * @return a string in the format: of the form {@code "<date>%<time> - <date>%<time>"}
     */
    public String toString()
    {
        return String.format("%s%%%s - %s%%%s", s_Start.date().toString(), s_Start.time().toString(),
        s_Finish.date().toString(), s_Finish.time().toString());
    }

    /** The start date-time of this shift. */
    private CalendarTime s_Start;

    /** The end date-time of this shift. */
    private CalendarTime s_Finish;
}
