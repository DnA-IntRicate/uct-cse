import java.io.IOException;

/**
 * Base class for all knowledge base implementations.
 *
 * This class is {@code abstract} and cannot be instantiated directly!
 *
 * @see Statement
 * @see KnowledgeBaseAVLTree
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public abstract class KnowledgeBase
{
    /**
     * Constructs a new {@link KnowledgeBase}.
     *
     * @param filePath the path to the knowledge base textfile
     *
     * @throws IOException throws when the knowledge base file fails to load
     */
    public KnowledgeBase(String filePath) throws IOException
    {
        m_KnowledgeBasePath = filePath;
        LoadKnowledgeBase();
    }

    /**
     * Loads the knowledge base from the textfile path supplied during instantiation of this object.
     *
     * @throws IOException throws when the knowledge base file fails to load
     */
    public abstract void LoadKnowledgeBase() throws IOException;

    /**
     * Search for a {@link Statement} in the {@link KnowledgeBase} by {@code term}.
     *
     * @param term the term to search for in the {@link KnowledgeBase}
     * @return the {@link Statement} found matching the {@code term} given, or {@code null} if nothing was found
     */
    public abstract Statement LookupStatement(String term);

    /**
     * Gets the path to the knowledge base textfile that this instance was loaded from.
     *
     * @return the path to the knowledge base textfile
     */
    public String GetKnowledgeBasePath() { return m_KnowledgeBasePath; }

    /** The path to the knowledge base. */
    protected String m_KnowledgeBasePath;
}
