/**
 * Base class for different types of people storing their basic info for use in {@link Question3}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Student
 */
public class Person
{
    /**
     * Create a new {@link Person} with the given {@code name}, {@code age} and {@code gender}.
     *
     * @param name the name of the person
     * @param age the age of the person
     * @param gender the gender of the person
     */
    public Person(String name, int age, String gender)
    {
        m_Name = name;
        m_Age = age;
        m_Gender = gender;
    }

    /**
     * Copy constructor.
     *
     * @param other the {@link Person} to copy
     */
    public Person(final Person other)
    {
        this(other.m_Name, other.m_Age, other.m_Gender);
    }

    /**
     * Get the name of this person.
     *
     * @return the name of this person
     */
    public String getName() { return m_Name; }

    /**
     * Set the name of this person.
     *
     * @param name the new name to set
     */
    public void setName(String name) { m_Name = name; }

    /**
     * Get the gender of this person.
     *
     * @return the gender of this person
     */
    public String getGender() { return m_Gender; }

    /**
     * Set the gender of this person.
     *
     * @param gender the new gender to set
     */
    public void setGender(String gender) { m_Gender = gender; }

    /**
     * Get the age of this person.
     *
     * @return the age of this person
     */
    public int getAge() { return m_Age; }

    /**
     * Set the age of this person.
     *
     * @param age the new age to set
     */
    public void setAge(int age) { m_Age = age; }

    // The name of this person.
    private String m_Name;

    // The age of this person.
    private int m_Age;

    // The gender of this person.
    private String m_Gender;
}
