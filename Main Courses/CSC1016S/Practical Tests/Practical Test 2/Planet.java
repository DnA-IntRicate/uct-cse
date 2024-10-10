// Adam Foflonker
// FFLADA001
// Practical Test 2
// 10 October 2024

public class Planet
{
    public Planet(String name, double mass, double density)
    {
        m_Name = name;
        m_Mass = mass;
        m_Density = density;
    }

    public String getName() { return m_Name; }

    public double getMass() { return m_Mass; }

    public double getDensity() { return m_Density; }

    @Override
    public String toString()
    {
        String mass = Double.toString(m_Mass);
        String density = Double.toString(m_Density);

        return String.format("%s has mass %s and density %s", m_Name, mass, density);
    }

    @Override
    public boolean equals(Object obj)
    {
        if (!(obj instanceof Planet))
            return false;

        Planet other = (Planet)obj;
        return m_Name.equals(other.m_Name) /*&& (m_Mass == other.m_Mass) && (m_Density == other.m_Density)*/;
    }

    private String m_Name;
    private double m_Mass;
    private double m_Density;
}
