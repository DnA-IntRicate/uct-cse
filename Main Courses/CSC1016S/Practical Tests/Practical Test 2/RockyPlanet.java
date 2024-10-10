// Adam Foflonker
// FFLADA001
// Practical Test 2
// 10 October 2024

public class RockyPlanet extends Planet
{
    public RockyPlanet(String name, double mass, double density, int numMoons)
    {
        super(name, mass, density);
        m_NumMoons = numMoons;
    }

    public int getNumMoons() { return m_NumMoons; }

    @Override
    public String toString()
    {
        return String.format("Rocky planet %s, and number of moons is %d", super.toString(), m_NumMoons);
    }

    private int m_NumMoons;
}
