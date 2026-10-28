import java.util.Scanner;

/**
 * Represents an statement in a knowledge base for use in {@link GenericsKbArrayApp} and {@link GenericsKbBSTApp}.
 *
 * @see KnowledgeBase
 * @see KnowledgeBaseArray
 * @see KnowledgeBaseBST
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public class Statement implements Comparable<Statement>
{
    /**
     * Constructs a new {@link Statement} from the given {@code entryStr}.
     * The {@code entryStr} must be in the format: <pre>{@code "<term>\t<sentence>\t<confidence>"}</pre>
     *
     * @param entryStr the string to construct this {@link Statement} from
     */
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
     * Copy constructor. Creates a new {@link Statement} as a direct copy of {@code other}
     *
     * @param other the {@link Statement} to make the new copy of
     */
    public Statement(final Statement other)
    {
        m_Term = other.m_Term;
        m_Sentence = other.m_Sentence;
        m_Confidence = other.m_Confidence;
    }

    /**
     * Default constructor.
     *
     * If only Java supported the 'default' keyword like C++...
     */
    public Statement()
    {
        m_Term = "";
        m_Sentence = "";
        m_Confidence = 0.0;
    }

    /**
     * Get this statement's {@code term}.
     *
     * @return this statement's {@code term} as a string.
     */
    public String GetTerm() { return m_Term; }

    /**
     * Set this statement's {@code term}.
     *
     * @param term the new term to set
     */
    public void SetTerm(String term) { m_Term = term; }

    /**
     * Get this statement's {@code sentence} as a string.
     *
     * @return this statement's {@code sentence} as a string
     */
    public String GetSentence() { return m_Sentence; }

    /**
     * Set this statement's {@code sentence}.
     *
     * @param sentence the new {@code sentence} to set
     */
    public void SetSentence(String sentence) { m_Sentence = sentence; }

    /**
     * Get this statement's {@code confidence level} as a double.
     *
     * @return this statement's {@code confidence level} as a double
     */
    public double GetConfidence() { return m_Confidence; }

    /**
     * Set this statement's {@code confidence level}. Value is clamped between {@code 0.0} and {@code 1.0}.
     *
     * @param confidence the new {@code confidence level} to set
     */
    public void SetConfidence(double confidence) { m_Confidence = Math.clamp(confidence, 0.0, 1.0); }

    /**
     * Checks for equality between this {@link Statement} and {@code other}.
     *
     * @return {@code true} if this statement equals other, {@code false} otherwise
     */
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

    // This statement's term
    private String m_Term;

    // This statement's sentence
    private String m_Sentence;

    // This statement's confidence level
    private double m_Confidence;
}
