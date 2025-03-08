import java.util.Iterator;
import java.util.Stack;

/**
 * Binary search tree.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 06/03/25
 */
public class BinarySearchTree <_Ty extends Comparable<_Ty>> implements Iterable<BinarySearchTree<_Ty>.Node>
{
    public class Node
    {
        public Node(_Ty value)
        {
            this.Value = value;
            this.Left = null;
            this.Right = null;
        }

        public _Ty Value;
        public Node Left;
        public Node Right;
    }

    /**
     * Performs an Inorder traversal.
     */
    public class BSTIterator implements Iterator<Node>
    {
        public BSTIterator(Node root)
        {
            m_NodeStack = new Stack<Node>();
            PushLeft(root);
        }

        @Override
        public boolean hasNext()
        {
            return !m_NodeStack.isEmpty();
        }

        @Override
        public Node next()
        {
            Node node = m_NodeStack.pop();
            PushLeft(node.Right);

            return node;
        }

        private void PushLeft(Node node)
        {
            while (node != null)
            {
                m_NodeStack.push(node);
                node = node.Left;
            }
        }

        private Stack<Node> m_NodeStack;
    }

    public BinarySearchTree()
    {
        m_Root = null;
    }

    public void Insert(_Ty value)
    {
        m_Root = InsertValueRootedAt(m_Root, value);
    }

    public Node Find(_Ty value)
    {
        return FindNodeWithValue(m_Root, value);
    }

    public boolean Empty()
    {
        return m_Root == null;
    }

    @Override
    public Iterator<Node> iterator()
    {
        return new BSTIterator(m_Root);
    }

    public Node GetRoot() { return m_Root; }

    private Node InsertValueRootedAt(Node root, _Ty value)
    {
        if (root == null)
            return new Node(value);

        if (value.compareTo(root.Value) < 0)
            root.Left = InsertValueRootedAt(root.Left, value);
        else
            root.Right = InsertValueRootedAt(root.Right, value);

        return root;
    }

    private Node FindNodeWithValue(Node root, _Ty value)
    {
        if (root == null)
            return null;

        if (value.equals(root.Value))
            return root;

        if (value.compareTo(root.Value) < 0)
            return FindNodeWithValue(root.Left, value);

        return FindNodeWithValue(root.Right, value);
    }

    private Node m_Root;
}
