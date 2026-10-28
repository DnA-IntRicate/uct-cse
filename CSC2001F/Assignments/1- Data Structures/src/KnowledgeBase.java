import java.util.ArrayList;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

/**
 * Base class for all knowledge base implementations.
 *
 * This class is {@code abstract} and cannot be instantiated directly!
 *
 * @see Statement
 * @see KnowledgeBaseArray
 * @see KnowledgeBaseBST
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
     */
    public KnowledgeBase(String filePath)
    {
        m_KnowledgeBasePath = filePath;
        LoadKnowledgeBase();
    }

    /**
     * Loads the knowledge base from the textfile path supplied during instantiation of this object.
     *
     * @return {@code true} if the knowledge base textfile was loaded successfully, {@code false} otherwise
     */
    public abstract boolean LoadKnowledgeBase();

    /**
     * Overwrites the original knowledge base textfile with this instance's data.
     *
     * @return {@code true} if the knowledge base textfile was written-to successfully, {@code false} otherwise
     */
    public abstract boolean WriteKnowledgeBase();

    /**
     * Search for a {@link Statement} in the {@link KnowledgeBase} by {@code term}.
     *
     * @param term the term to search for in the {@link KnowledgeBase}
     * @return the {@link Statement} found matching the {@code term} given, or {@code null} if nothing was found
     */
    public abstract Statement LookupStatement(String term);

    /**
     * Search for a {@link Statement} in the {@link KnowledgeBase} by {@code term} and {@code sentence}
     *
     * @param term the term to search for in the {@link KnowledgeBase}
     * @param sentence the sentence to search for in the {@link KnowledgeBase}
     * @return the {@link Statement} found matching the {@code term} and {@code sentence} given,
     * or {@code null} if nothing was found
     */
    public abstract Statement LookupStatement(String term, String sentence);

    /**
     * Searches for all statements in the {@link KnowledgeBase} matching {@code term}.
     *
     * @param term the term to search for in the {@link KnowledgeBase}
     * @return an {@link ArrayList} of {@link Statement} of all the matching statements found matching {@code term},
     * or an empty {@link ArrayList} if none were found
     */
    public abstract ArrayList<Statement> LookupAllStatements(String term);

    /**
     * Searches for all statements in the {@link KnowledgeBase} matching the partial term {@code termPattern}.
     *
     * @param termPattern the partial term to search for in the {@link KnowledgeBase}
     * @return an {@link ArrayList} of {@link Statement} of all the matching statements found matching {@code term},
     * or an empty {@link ArrayList} if none were found
     */
    public abstract ArrayList<Statement> LookupAllStatementsByPartialTerm(String termPattern);

    /**
     * Add the given {@link Statement} {@code st} to the {@link KnowledgeBase}.
     *
     * @param st the statement to add to the {@link KnowledgeBase}
     * @return {@code true} if the statement was added successfully, {@code false} otherwise
     */
    public abstract boolean AddStatement(final Statement st);

    /**
     * Find and update the found {@link Statement} in the {@link KnowledgeBase}.
     *
     * @param oldSt the {@link Statement} to find
     * @param newSt the new {@link Statement} to update {@code oldSt} with
     * @return {@code true} if the statement was updated successfully, {@code false} otherwise
     */
    public abstract boolean UpdateStatement(final Statement oldSt, final Statement newSt);

    /**
     * Gets the path to the knowledge base textfile that this instance was loaded from.
     *
     * @return the path to the knowledge base textfile
     */
    public String GetKnowledgeBasePath() { return m_KnowledgeBasePath; }

    /**
     * Determines the number of lines in a textfile.
     *
     * @return the number of lines in the knowledge base textfile
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

    /** The path to the knowledge base. */
    protected String m_KnowledgeBasePath;
}
