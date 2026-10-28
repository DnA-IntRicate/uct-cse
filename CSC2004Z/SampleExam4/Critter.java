/**
 * Represents a critter for use in {@link Population}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 01/03/25
 */
public class Critter
{
    public Critter(String geneticCode)
    {
        m_GeneticCode = geneticCode;
    }

    public String GetGeneticCode() { return m_GeneticCode; }

    private String m_GeneticCode;
}
