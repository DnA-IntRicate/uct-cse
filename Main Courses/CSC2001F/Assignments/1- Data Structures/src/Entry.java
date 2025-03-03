import java.util.Scanner;

/**
 * Represents an entry in the knowledge base.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public class Entry
{
    public Entry(String entryStr)
    {
        try (Scanner scanner = new Scanner(entryStr))
        {
            scanner.useDelimiter("\t");
            m_Term = scanner.next();
            m_Statement = scanner.next();
            m_Confidence = scanner.nextDouble();
        }
    }

    /**
     * Copy ctor.
     */
    public Entry(final Entry other)
    {
        m_Term = other.m_Term;
        m_Statement = other.m_Statement;
        m_Confidence = other.m_Confidence;
    }

    public String GetTerm() { return m_Term; }
    public void SetTerm(String term) { m_Term = term; }

    public String GetStatement() { return m_Statement; }
    public void SetStatement(String sentence) { m_Statement = sentence; }

    public double GetConfidence() { return m_Confidence; }
    public void SetConfidence(double confidence) { m_Confidence = confidence; }

    @Override
    public boolean equals(Object other)
    {
        if (!(other instanceof Entry))
            return false;

        Entry myOther = (Entry)other;
        return m_Term.equals(myOther.m_Term) && m_Statement.equals(myOther.m_Statement) &&
            (m_Confidence == myOther.m_Confidence);
    }

    private String m_Term;
    private String m_Statement;
    private double m_Confidence;
}

