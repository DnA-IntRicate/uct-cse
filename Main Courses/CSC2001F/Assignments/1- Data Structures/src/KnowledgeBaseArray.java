import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

/**
 * Something...
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public class KnowledgeBaseArray extends KnowledgeBase
{
    public KnowledgeBaseArray(String filePath) throws IOException
    {
        super(filePath);
        LoadKnowledgeBase();
    }

    /**
     *
     */
    @Override
    public Entry LookupEntry(String term)
    {
        // Linear search because the knowledge-base is unsorted
        for (Entry e : m_Entries)
        {
            if (e.GetTerm().toLowerCase().equals(term.toLowerCase()))
                return e;
        }

        return null;
    }

    /**
     *
     */
    @Override
    public Entry LookupEntry(String term, String sentence)
    {
        // Linear search because the knowledge-base is unsorted
        for (final Entry e : m_Entries)
        {
            if (e.GetTerm().toLowerCase().equals(term.toLowerCase()) && e.GetSentence().toLowerCase().equals(sentence.toLowerCase()))
                return e;
        }

        return null;
    }

    /**
     *
     */
    @Override
    public boolean AddEntry(final Entry entry)
    {
        // Append the file
        try (FileWriter writer = new FileWriter(m_KnowledgeBasePath, true))
        {
            writer.write(String.format("%s\t%s\t%f\n", entry.GetTerm(), entry.GetSentence(), entry.GetConfidence()));
            return LoadKnowledgeBase();
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        return false;
    }

    /**
     *
     */
    @Override
    public boolean UpdateEntry(final Entry oldEntry, final Entry newEntry)
    {
        for (int i = 0; i < m_Entries.length; ++i)
        {
            if (m_Entries[i].equals(oldEntry))
            {
                m_Entries[i] = new Entry(newEntry);
                return WriteKnowledgeBase();
            }
        }

        return false;
    }

    // TODO: Move me to the parent class.
    private static int NumLinesInFile(String filePath)
    {
        int res = 0;
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath)))
        {
            while (reader.readLine() != null)
                res++;
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        return res;
    }

    private boolean LoadKnowledgeBase()
    {
        m_Entries = null;
        m_Entries = new Entry[NumLinesInFile(m_KnowledgeBasePath)];

        try (BufferedReader reader = new BufferedReader(new FileReader(m_KnowledgeBasePath)))
        {
            String lineBuf = "";
            for (int i = 0; (i < m_Entries.length) && (lineBuf != null); ++i)
            {
                lineBuf = reader.readLine();
                m_Entries[i] = new Entry(lineBuf);
            }

            return true;
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        return false;
    }

    // TODO: Move me to the parent class.
    private boolean WriteKnowledgeBase()
    {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(m_KnowledgeBasePath)))
        {
            for (final Entry e : m_Entries)
            {
                String content = String.format("%s\t%s\t%f", e.GetTerm(), e.GetSentence(), e.GetConfidence());
                writer.write(content);
                writer.newLine();
            }

            return true;
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        return false;
    }

    private Entry[] m_Entries;
}
