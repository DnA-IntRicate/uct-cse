import java.util.List;
import java.util.ArrayList;

/**
 * Represents a basic employee that contains their name, uid and their worked shifts.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 11/09/24
 */
public class Employee
{
    /**
     * Creates a new {@link Employee} from the given {@code name} and {@code uid}.
     *
     * @param name the name of the employee
     * @param uid the unique identifier (UID) of the employee
     */
    public Employee(String name, String uid)
    {
        m_CurrentShiftStart = null;
        m_Name = name;
        m_Uid = uid;
        m_Shifts = new ArrayList<Shift>();
    }

    /**
     * Record that this employee has begun a shift on the given date and at the given time.
     *
     * @param d the {@link Date} of the start of the shift
     * @param t the {@link Time} of the start of the shift
     */
    public void signIn(Date d, Time t)
    {
        m_CurrentShiftStart = new CalendarTime(d, t);
    }

    /**
     * Record that this employee has completed a shift on the given date and at the given time.
     *
     * @param d the {@link Date} of the end of the shift
     * @param t the {@link Time} of the end of the shift
     */
    public void signOut(Date d, Time t)
    {
        m_Shifts.add(new Shift(m_CurrentShiftStart, new CalendarTime(d, t)));
        m_CurrentShiftStart = null;
    }

    /**
     * Returns the total time (hours and minutes) worked during the given {@link Week}.
     *
     * @param w the {@link Week} to check
     * @return the total time worked during {@code w} as a {@link Duration}
     */
    public Duration hours(Week w)
    {
        Duration res = Duration.ZERO;
        for (final Shift s : m_Shifts)
        {
            if (s.inWeek(w))
                res.add(s.length());
        }

        return res;
    }

    /**
     * Checks whether this employee is present (has signed-in and not yet signed-out).
     *
     * @return {@code true} if present, otherwise {@code false}
     */
    public boolean present()
    {
        return m_CurrentShiftStart != null;
    }

    /**
     * Checks whether this employee is present (has signed-in and not yet signed-out) on the given {@link Date}.
     *
     * @param d the {@link Date} to check
     * @return {@code true} if present on the given date {@code d}, otherwise {@code false}
     */
    public boolean present(Date d)
    {
        return (m_CurrentShiftStart != null) && (m_CurrentShiftStart.date().compareTo(d) == 0);
    }

    /**
     * Checks if this employee worked on the given {@link Date}.
     *
     * @param d the {@link Date} to check
     * @return {@code true} if worked on the given date {@code d}, otherwise {@code false}
     */
    public boolean worked(Date d)
    {
        for (final Shift s : m_Shifts)
        {
            if (s.includesDate(d))
                return true;
        }

        return false;
    }

    /**
     * Checks if this employee worked during the given {@link Week}.
     *
     * @param w the {@link Week} to check
     * @return {@code true} if worked during the given week {@code w}, otherwise {@code false}
     */
    public boolean worked(Week w)
    {
        for (final Shift s : m_Shifts)
        {
            if (s.inWeek(w))
                return true;
        }

        return false;
    }

    /**
     * Get this employee's name.
     *
     * @return this employee's name
     */
    public String name() { return m_Name; }

    /**
     * Get this employee's UID.
     *
     * @return this employee's UID
     */
    public String UID() { return m_Uid; }

    /**
     * Returns a list of the shifts worked by this employee during the given {@link Week}.
     *
     * @return the list of shifts worked by this employee during the given week {@code w}
     */
    public List<Shift> get(Week w)
    {
        List<Shift> res = new ArrayList<Shift>();
        for (final Shift s : m_Shifts)
        {
            if (s.inWeek(w))
                res.add(s);
        }

        return res;
    }

    /**
     * Return a list of the shifts worked by this employee on or accross the given {@link Date}.
     *
     * @return the list of shifts worked by this employee on or accross the given date {@code d}
     */
    public List<Shift> get(Date d)
    {
        List<Shift> res = new ArrayList<Shift>();
        for (final Shift s : m_Shifts)
        {
            if (s.includesDate(d))
                res.add(s);
        }

        return res;
    }

    /** Stores the start-time of this employee's current shift.
     * If this employee is not currently working a shift then this object will be {@code null}.
     */
    private CalendarTime m_CurrentShiftStart;

    /** The name of this employee */
    private String m_Name;

    /** The unique identifier of this employee */
    private String m_Uid;

    /** The shifts that this employee has worked */
    private List<Shift> m_Shifts;
}
