import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

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
        LoadKnowledgeBase();
    }

    /**
     *
     */
    public abstract boolean LoadKnowledgeBase();

    /**
     *
     */
    public abstract boolean WriteKnowledgeBase();

    /**
     *
     */
    public abstract Entry LookupEntry(String term);

    /**
     *
     */
    public abstract Entry LookupEntry(String term, String sentence);

    /**
     *
     */
    public abstract boolean AddEntry(final Entry entry);

    /**
     *
     */
    public abstract boolean UpdateEntry(final Entry oldEntry, final Entry newEntry);

    /**
     *
     */
    public String GetKnowledgeBasePath() { return m_KnowledgeBasePath; }

    /**
     *
     */
    protected int CalcNumLinesInKnowledgeBase()
    {
        int res = 0;
        try (BufferedReader reader = new BufferedReader(new FileReader(m_KnowledgeBasePath)))
        {
            while (reader.readLine() != null)
                res++;
        }
        catch (IOException e)
        {
            return -1;
        }

        return res;
    }

    protected String m_KnowledgeBasePath;
}
