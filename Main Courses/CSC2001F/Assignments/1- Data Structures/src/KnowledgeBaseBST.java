import java.util.ArrayList;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

/**
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public final class KnowledgeBaseBST extends KnowledgeBase
{
    public KnowledgeBaseBST(String filePath)
    {
        super(filePath);
    }

    /**
     *
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
     *
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
     *
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

            if (stTerm.contains(termPattern))
                res.add(node.Value);
        }

        return res;
    }

    @Override
    public boolean AddStatement(Statement st)
    {
        m_StatementTree.Insert(st);
        return WriteKnowledgeBase();
    }

    @Override
    public boolean UpdateStatement(Statement oldSt, Statement newSt)
    {
        var node = m_StatementTree.Find(oldSt);
        if (node == null)
            return false;

        node.Value = new Statement(newSt);
        return WriteKnowledgeBase();
    }

    private BinarySearchTree<Statement> m_StatementTree;
}
