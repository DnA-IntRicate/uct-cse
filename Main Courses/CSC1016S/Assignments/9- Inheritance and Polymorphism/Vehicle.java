/**
 * Base class for all vehicles for use in {@link Question3}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Car
 * @see Student
 */
public class Vehicle
{
    /**
     * Create a new {@link Vehicle} with the given {@code numCylinders}, {@code manufacturer} and {@code owner}.
     *
     * @param numCylinders the number of cylinders of the vehicle
     * @param manufacturer the manufacturer of the vehicle
     * @param owner the owner of the vehicle of type {@link Student}
     */
    public Vehicle(int numCylinders, String manufacturer, Student owner)
    {
        m_NumCylinders = numCylinders;
        m_Manufacturer = manufacturer;
        m_Owner = owner;
    }

    /**
     * Copy constructor.
     *
     * @param other the {@link Vehicle} to copy
     */
    public Vehicle(final Vehicle other)
    {
        this(other.m_NumCylinders, other.m_Manufacturer, other.m_Owner);
    }

    /**
     * Returns a string representation of this vehicle.
     *
     * @return a string representation of this vehicle in the format:
     *
     * {@code "<manufacturer>, <numCylinders> cylinders, owned by <student.name>, a <student.age>-year old
     * <student.gender> studying <student.program> at <student.institution>. <student.name> likes <student.hobbies>."}
     */
    public String toString()
    {
        String ownerStr = String.format("%s, a %d-year old %s studying %s at %s. %s likes %s.",
            m_Owner.getName(), m_Owner.getAge(), m_Owner.getGender(), m_Owner.getProgramOfStudy(),
            m_Owner.getNameOfInstitution(), m_Owner.getName(), m_Owner.getHobbies());

        return String.format("%s, %d cylinders, owned by %s", m_Manufacturer, m_NumCylinders, ownerStr);
    }

    // The number of cylinders of this vehicle.
    private int m_NumCylinders;

    // The manufacturer of this vehicle.
    private String m_Manufacturer;

    // The Student owner of this vehicle.
    private Student m_Owner;
}
