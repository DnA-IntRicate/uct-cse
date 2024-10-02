/**
 * TODO: Person
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Person
{
    public Person(String name, int age, String gender)
    {
        m_Name = name;
        m_Age = age;
        m_Gender = gender;
    }

    public Person(final Person other)
    {
        this(other.m_Name, other.m_Age, other.m_Gender);
    }

    public String getName() { return m_Name; }
    public void setName(String name) { m_Name = name; }

    public String getGender() { return m_Gender; }
    public void setGender(String gender) { m_Gender = gender; }

    public int getAge() { return m_Age; }
    public void setAge(int age) { m_Age = age; }

    private String m_Name;
    private int m_Age;
    private String m_Gender;

}
