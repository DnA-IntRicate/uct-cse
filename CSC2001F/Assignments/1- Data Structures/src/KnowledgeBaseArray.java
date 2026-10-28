import java.util.ArrayList;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Implementation of {@link KnowledgeBase} using an array.
 *
 * @see KnowledgeBase
 * @see KnowledgeBaseBST
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public final class KnowledgeBaseArray extends KnowledgeBase
{
    /**
     * Constructs a new {@link KnowledgeBase}.
     *
     * @param filePath the path to the knowledge base textfile
     */
    public KnowledgeBaseArray(String filePath)
    {
        super(filePath);
    }

    /**
     * Loads the knowledge base from the textfile path supplied during instantiation of this object.
     *
     * @return {@code true} if the knowledge base textfile was loaded successfully, {@code false} otherwise
     */
    @Override
    public boolean LoadKnowledgeBase()
    {
        m_Statements = null;
        m_Statements = new Statement[CalcNumLinesInKnowledgeBase()];

        try
        {
            int i = 0;
            for (String lineBuf : Files.readAllLines(Paths.get(m_KnowledgeBasePath)))
            {
                if (lineBuf == null)
                    break;

                m_Statements[i++] = new Statement(lineBuf);
            }

            return true;
        }
        catch (IOException e)
        {
            return false;
        }
    }

    /**
     * Overwrites the original knowledge base textfile with this instance's data.
     *
     * @return {@code true} if the knowledge base textfile was written-to successfully, {@code false} otherwise
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
     * Search for a {@link Statement} in the {@link KnowledgeBase} by {@code term}.
     *
     * @param term the term to search for in the {@link KnowledgeBase}
     * @return the {@link Statement} found matching the {@code term} given, or {@code null} if nothing was found
     */
    @Override
    public Statement LookupStatement(String term)
    {
        Statement res = null;

        // Linear search because the knowledge-base is unsorted
        for (Statement st : m_Statements)
        {
            if (st.GetTerm().toLowerCase().equals(term.toLowerCase()))
                res = (res == null) ? st : ((res.GetConfidence() < st.GetConfidence()) ? st : res);
        }

        return res;
    }

    /**
     * Search for a {@link Statement} in the {@link KnowledgeBase} by {@code term} and {@code sentence}
     *
     * @param term the term to search for in the {@link KnowledgeBase}
     * @param sentence the sentence to search for in the {@link KnowledgeBase}
     * @return the {@link Statement} found matching the {@code term} and {@code sentence} given,
     * or {@code null} if nothing was found
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
     * Searches for all statements in the {@link KnowledgeBase} matching {@code term}.
     *
     * @param term the term to search for in the {@link KnowledgeBase}
     * @return an {@link ArrayList} of {@link Statement} of all the matching statements found matching {@code term},
     * or an empty {@link ArrayList} if none were found
     */
    public ArrayList<Statement> LookupAllStatements(String term)
    {
        ArrayList<Statement> res = new ArrayList<Statement>();

        // Linear search because the knowledge-base is unsorted
        for (Statement st : m_Statements)
        {
            if (st.GetTerm().toLowerCase().equals(term.toLowerCase()))
                res.add(st);
        }

        return res;
    }

    /**
     * Searches for all statements in the {@link KnowledgeBase} matching the partial term {@code termPattern}.
     *
     * @param termPattern the partial term to search for in the {@link KnowledgeBase}
     * @return an {@link ArrayList} of {@link Statement} of all the matching statements found matching {@code term},
     * or an empty {@link ArrayList} if none were found
     */
    public ArrayList<Statement> LookupAllStatementsByPartialTerm(String termPattern)
    {
        ArrayList<Statement> res = new ArrayList<Statement>();

        // Linear search because the knowledge-base is unsorted
        for (Statement st : m_Statements)
        {
            String stTerm = st.GetTerm().toLowerCase();
            termPattern = termPattern.toLowerCase();

            if (stTerm.equals(termPattern))
            {
                res.add(st);
                continue;
            }

            if (stTerm.length() < termPattern.length())
                continue;

            if (stTerm.substring(0, termPattern.length()).equals(termPattern))
                res.add(st);
        }

        return res;
   }

    /**
     * Add the given {@link Statement} {@code st} to the {@link KnowledgeBase}.
     *
     * @param st the statement to add to the {@link KnowledgeBase}
     * @return {@code true} if the statement was added successfully, {@code false} otherwise
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
     * Find and update the found {@link Statement} in the {@link KnowledgeBase}.
     *
     * @param oldSt the {@link Statement} to find
     * @param newSt the new {@link Statement} to update {@code oldSt} with
     * @return {@code true} if the statement was updated successfully, {@code false} otherwise
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

    // The statement array
    private Statement[] m_Statements;
}
