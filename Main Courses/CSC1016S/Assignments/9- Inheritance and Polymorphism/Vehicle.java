/**
 * TODO: Vehicle
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Vehicle
{
    public Vehicle(int numCylinders, String manufacturer, Student owner)
    {
        m_NumCylinders = numCylinders;
        m_Manufacturer = manufacturer;
        m_Owner = owner;
    }

    public Vehicle(final Vehicle other)
    {
        this(other.m_NumCylinders, other.m_Manufacturer, other.m_Owner);
    }

    public String toString()
    {
        String ownerStr = String.format("%s, a %d-year old %s studying %s at %s. %s likes %s.",
            m_Owner.getName(), m_Owner.getAge(), m_Owner.getGender(), m_Owner.getProgramOfStudy(),
            m_Owner.getNameOfInstitution(), m_Owner.getName(), m_Owner.getHobbies());

        return String.format("%s, %d cylinders, owned by %s", m_Manufacturer, m_NumCylinders, ownerStr);
    }

    private int m_NumCylinders;
    private String m_Manufacturer;
    private Student m_Owner;
}
