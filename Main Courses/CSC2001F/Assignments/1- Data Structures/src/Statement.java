import java.util.Scanner;

/**
 * Represents an entry in the knowledge base.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public class Statement implements Comparable<Statement>
{
    public Statement(String entryStr)
    {
        try (Scanner scanner = new Scanner(entryStr))
        {
            scanner.useDelimiter("\t");
            m_Term = scanner.next();
            m_Sentence = scanner.next();
            m_Confidence = scanner.nextDouble();
        }
    }

    /**
     * Copy ctor.
     */
    public Statement(final Statement other)
    {
        m_Term = other.m_Term;
        m_Sentence = other.m_Sentence;
        m_Confidence = other.m_Confidence;
    }

    /**
     * Default ctor.
     */
    public Statement()
    {
        m_Term = "";
        m_Sentence = "";
        m_Confidence = 0.0;
    }

    public String GetTerm() { return m_Term; }
    public void SetTerm(String term) { m_Term = term; }

    public String GetSentence() { return m_Sentence; }
    public void SetSentence(String sentence) { m_Sentence = sentence; }

    public double GetConfidence() { return m_Confidence; }
    public void SetConfidence(double confidence) { m_Confidence = confidence; }

    @Override
    public boolean equals(Object other)
    {
        if (!(other instanceof Statement))
            return false;

        Statement myOther = (Statement)other;
        return m_Term.equals(myOther.m_Term) && m_Sentence.equals(myOther.m_Sentence) &&
            (m_Confidence == myOther.m_Confidence);
    }

    /**
     * Compares this {@link Statement} to the specified object {@code other} for order.
     * Returns a negative integer, zero or a positive integer if this object's {@code Term}
     * is less than, equal to, or greater than the specified object.
     *
     * If the two objects terms are equal, it compares this object's {@code Sentence} to other's instead.
     *
     * @param other the {@link Statement} to compare this object to.
     * @return a negative integer, zero or a positive integer.
     */
    @Override
    public int compareTo(Statement other)
    {
        if (m_Term.equals(other.m_Term))
            return m_Sentence.compareTo(other.m_Sentence);

        return m_Term.compareTo(other.m_Term);
    }

    private String m_Term;
    private String m_Sentence;
    private double m_Confidence;
}
