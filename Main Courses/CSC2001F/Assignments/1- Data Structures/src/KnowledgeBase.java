/**
 * Base class for all knowledge bases.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */

public abstract class KnowledgeBase
{
    public KnowledgeBase(String filePath)
    {
        m_KnowledgeBasePath = filePath;
    }

    /**
     *
     */
    public abstract Entry LookupEntry(String term);

    /**
     *
     */
    public abstract Entry LookupEntry(String term, String sentence);

    /*
     *
     */
    public abstract boolean AddEntry(final Entry entry);

    /*
     *
     */
    public abstract boolean UpdateEntry(final Entry oldEntry, final Entry newEntry);

    /*
     *
     */
    public String GetKnowledgeBasePath() { return m_KnowledgeBasePath; }

    protected String m_KnowledgeBasePath;
}
