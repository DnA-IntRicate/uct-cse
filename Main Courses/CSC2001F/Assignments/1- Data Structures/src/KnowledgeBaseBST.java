import java.util.ArrayList;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

/**
 * Implementation of {@link KnowledgeBase} using a {@link BinarySearchTree}.
 *
 * @see BinarySearchTree
 * @see KnowledgeBase
 * @see KnowledgeBaseArray
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public final class KnowledgeBaseBST extends KnowledgeBase
{
    /**
     * Constructs a new {@link KnowledgeBase}.
     *
     * @param filePath the path to the knowledge base textfile
     */
    public KnowledgeBaseBST(String filePath)
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
        m_StatementTree = new BinarySearchTree<Statement>();

        try (BufferedReader reader = new BufferedReader(new FileReader(m_KnowledgeBasePath)))
        {
            while (true)
            {
                String lineBuf = reader.readLine();
                if (lineBuf == null)
                    break;

                m_StatementTree.Insert(new Statement(lineBuf));
            }

            return true;
        }
        catch (IOException e)
        {
            return false;
        }
    }

    /**
     * This function is unimplemented for BSTs.
     * When a BST is created, it's structure automatically sorts all data inserted into it.
     * Since the BST is naturally sorted, when rewriting the KnowledgeBase textfile, the file will now also have
     * all of its statements sorted. When calling {@link #LoadKnowledgeBase()} on a KnowledgeBase that
     * is already sorted, this creates an unbalanced tree only inserting elements to the right of each
     * node, effectively creating a linked list. This also will likely result in
     * {@link BinarySearchTree#Insert(Comparable)} causing a stack overflow due to the height of the tree
     * now being O(n) in this case instead of O(log n).
     *
     * @deprecated
     */
    @Override
    @Deprecated
    public boolean WriteKnowledgeBase()
    {
        return true;
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

        // Performs an Inorder traversal iteration over the BST
        for (final var node : m_StatementTree)
        {
            // Finds the statement with the highest confidence score
            if (node.Value.GetTerm().toLowerCase().equals(term.toLowerCase()))
                res = (res == null) ? node.Value : ((res.GetConfidence() < node.Value.GetConfidence()) ? node.Value : res);
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
        // Performs an Inorder traversal iteration over the BST
        for (final var node : m_StatementTree)
        {
            if (node.Value.GetTerm().toLowerCase().equals(term.toLowerCase()) &&
                node.Value.GetSentence().toLowerCase().equals(sentence.toLowerCase()))
                return node.Value;
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

        // Performs an Inorder traversal iteration over the BST
        for (final var node : m_StatementTree)
        {
            if (node.Value.GetTerm().toLowerCase().equals(term.toLowerCase()))
                res.add(node.Value);
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

        // Performs an Inorder traversal iteration over the BST
        for (final var node : m_StatementTree)
        {
            String stTerm = node.Value.GetTerm().toLowerCase();
            termPattern = termPattern.toLowerCase();

            if (stTerm.equals(termPattern))
            {
                res.add(node.Value);
                continue;
            }

            if (stTerm.length() < termPattern.length())
                continue;

            if (stTerm.substring(0, termPattern.length()).equals(termPattern))
                res.add(node.Value);
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
    public boolean AddStatement(Statement st)
    {
        m_StatementTree.Insert(st);
        return WriteKnowledgeBase();
    }

    /**
     * Find and update the found {@link Statement} in the {@link KnowledgeBase}.
     *
     * @param oldSt the {@link Statement} to find
     * @param newSt the new {@link Statement} to update {@code oldSt} with
     * @return {@code true} if the statement was updated successfully, {@code false} otherwise
     */
    @Override
    public boolean UpdateStatement(Statement oldSt, Statement newSt)
    {
        var node = m_StatementTree.Find(oldSt);
        if (node == null)
            return false;

        node.Value = new Statement(newSt);
        return WriteKnowledgeBase();
    }

    // The binary search tree of statements
    private BinarySearchTree<Statement> m_StatementTree;
}
