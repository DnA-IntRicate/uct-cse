import java.nio.file.Files;
import java.nio.file.Paths;
import java.io.IOException;

/**
 * Implementation of {@link KnowledgeBase} using an {@link AVLTree}.
 *
 * @see AVLTree
 * @see KnowledgeBase
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public final class KnowledgeBaseAVLTree extends KnowledgeBase
{
    /**
     * Constructs a new {@link KnowledgeBase}.
     *
     * @param filePath the path to the knowledge base textfile
     *
     * @throws IOException throws when the knowledge base file fails to load
     */
    public KnowledgeBaseAVLTree(String filePath) throws IOException
    {
        super(filePath);
    }

    /**
     * Loads the knowledge base from the textfile path supplied during instantiation of this object.
     *
     * @throws IOException throws when the knowledge base file fails to load
     */
    @Override
    public void LoadKnowledgeBase() throws IOException
    {
        m_StatementTree = new AVLTree<String, Statement>();

        try
        {
            for (String lineBuf : Files.readAllLines(Paths.get(m_KnowledgeBasePath)))
            {
                if (lineBuf == null)
                    break;

                Statement st = new Statement(lineBuf);
                m_StatementTree.Insert(st.GetTerm(), st); // This is a bit inefficient memory-wise but, oh well.
            }
        }
        catch (IOException e)
        {
            throw e;
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
        var node = m_StatementTree.Find(term);
        if (node == null)
            return null;

        return node.Value;
    }

    // The AVL tree of statements
    // The key is the Term and the value is the Statement associated with that term
    private AVLTree<String, Statement> m_StatementTree;
}
