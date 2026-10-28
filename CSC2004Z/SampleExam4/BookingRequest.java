/**
 * Represents a booking request for use in {@link Bookings}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 28/02/25
 */
public class BookingRequest
{
    public BookingRequest(String bookingStr)
    {
        int idxDash = bookingStr.indexOf("-");
        m_Start = new Time(bookingStr.substring(0, idxDash - 1));
        m_End = new Time(bookingStr.substring(idxDash + 2));
    }

    public Time GetStart() { return m_Start; }
    public Time GetEnd() { return m_End; }

    /**
     * Checks if this booking is overlapping with {@code other}.
     *
     * @param other the booking to check for overlapping
     * @return {@code true} if this booking overlaps with {@code other}, {@code false} otherwise
     */
    public boolean IsOverlapping(final BookingRequest other)
    {
        if (this.equals(other))
            return true;

        return !((m_End.GetTimeMinutes() <= other.m_Start.GetTimeMinutes()) ||
            (m_Start.GetTimeMinutes() >= other.m_End.GetTimeMinutes()));
    }

    @Override
    public boolean equals(Object other)
    {
        if (!(other instanceof BookingRequest))
            return false;

        BookingRequest myOther = (BookingRequest)other;
        return m_Start.equals(myOther.m_Start) && m_End.equals(myOther.m_End);
    }

    private Time m_Start;
    private Time m_End;
}
