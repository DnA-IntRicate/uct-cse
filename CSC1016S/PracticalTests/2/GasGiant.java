// Adam Foflonker
// FFLADA001
// Practical Test 2
// 10 October 2024

public class GasGiant extends Planet
{
    public GasGiant(String name, double mass, double density, boolean hasRings)
    {
        super(name, mass, density);
        m_HasRings = hasRings;
    }

    public boolean hasRings() { return m_HasRings; }

    @Override
    public String toString()
    {
        if (m_HasRings)
            return String.format("Gas giant %s, and has rings", super.toString());

        return String.format("Gas giant %s, and does not have rings", super.toString());
    }

    private boolean m_HasRings;
}
