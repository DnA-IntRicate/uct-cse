import java.io.BufferedReader;
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

    // TODO: You know what, lets remove filewriting...
    @Override
    public boolean WriteKnowledgeBase()
    {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'WriteKnowledgeBase'");
    }

    // TODO: The highest confidence score statement must be returned!
    @Override
    public Statement LookupStatement(String term)
    {
        // Performs an Inorder traversal iteration over the BST
        for (final var node : m_StatementTree)
        {
            if (node.Value.GetTerm().toLowerCase().equals(term.toLowerCase()))
                return node.Value;
        }

        return null;
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

    // TODO: Make this just add a new statement without the filewriting
    @Override
    public boolean AddStatement(Statement st)
    {
        // Append the file, we write to the file first so that the order of the KB isn't changed by the
        // structure of the BST
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

    @Override
    public boolean UpdateStatement(Statement oldSt, Statement newSt)
    {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'UpdateStatement'");
    }

    private BinarySearchTree<Statement> m_StatementTree;
}
