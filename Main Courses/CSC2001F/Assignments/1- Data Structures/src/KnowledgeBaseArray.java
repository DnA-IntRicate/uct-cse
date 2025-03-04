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
    public KnowledgeBaseArray(String filePath)
    {
        super(filePath);
    }

    /**
     *
     */
    @Override
    public boolean LoadKnowledgeBase()
    {
        m_Statements = null;
        m_Statements = new Statement[CalcNumLinesInKnowledgeBase()];

        try (BufferedReader reader = new BufferedReader(new FileReader(m_KnowledgeBasePath)))
        {
            String lineBuf = "";
            for (int i = 0; (i < m_Statements.length) && (lineBuf != null); ++i)
            {
                lineBuf = reader.readLine();
                m_Statements[i] = new Statement(lineBuf);
            }

            return true;
        }
        catch (IOException e)
        {
            return false;
        }
    }

    /**
     *
     */
    @Override
    public boolean WriteKnowledgeBase()
    {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(m_KnowledgeBasePath)))
        {
            for (final Statement st : m_Statements)
            {
                String content = String.format("%s\t%s\t%f", st.GetTerm(), st.GetSentence(), st.GetConfidence());
                writer.write(content);
                writer.newLine();
            }

            return true;
        }
        catch (IOException e)
        {
            return false;
        }
    }

    /**
     *
     */
    @Override
    public Statement LookupStatement(String term)
    {
        // Linear search because the knowledge-base is unsorted
        for (Statement st : m_Statements)
        {
            if (st.GetTerm().toLowerCase().equals(term.toLowerCase()))
                return st;
        }

        return null;
    }

    /**
     *
     */
    @Override
    public Statement LookupStatement(String term, String sentence)
    {
        // Linear search because the knowledge-base is unsorted
        for (final Statement st : m_Statements)
        {
            if (st.GetTerm().toLowerCase().equals(term.toLowerCase()) &&
                st.GetSentence().toLowerCase().equals(sentence.toLowerCase()))
                return st;
        }

        return null;
    }

    /**
     *
     */
    @Override
    public boolean AddStatement(final Statement st)
    {
        // Append the file
        try (FileWriter writer = new FileWriter(m_KnowledgeBasePath, true))
        {
            writer.write(String.format("%s\t%s\t%f\n", st.GetTerm(), st.GetSentence(), st.GetConfidence()));
            return LoadKnowledgeBase();
        }
        catch (IOException e)
        {
            return false;
        }
    }

    /**
     *
     */
    @Override
    public boolean UpdateStatement(final Statement oldSt, final Statement newSt)
    {
        for (int i = 0; i < m_Statements.length; ++i)
        {
            if (m_Statements[i].equals(oldSt))
            {
                m_Statements[i] = new Statement(newSt);
                return WriteKnowledgeBase();
            }
        }

        return false;
    }

    private Statement[] m_Statements;
}
