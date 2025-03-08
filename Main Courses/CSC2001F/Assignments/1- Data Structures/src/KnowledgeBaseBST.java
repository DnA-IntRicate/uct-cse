import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
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
     *
     */
    @Override
    public boolean WriteKnowledgeBase()
    {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(m_KnowledgeBasePath)))
        {
            for (final var node : m_StatementTree)
            {
                Statement st = node.Value;
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
