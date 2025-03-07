/**
 * Binary search tree.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 06/03/25
 */
public class BinarySearchTree <_Ty extends Comparable<_Ty>>
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

        if (value.compareTo(root.Value) == 0)
            return root;

        if (value.compareTo(root.Value) < 0)
            return FindNodeWithValue(root.Left, value);

        return FindNodeWithValue(root.Right, value);
    }

    private Node m_Root;
}
