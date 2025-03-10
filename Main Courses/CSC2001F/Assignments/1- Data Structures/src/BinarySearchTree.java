import java.util.Iterator;
import java.util.Stack;

/**
 * A basic implementation of a binary search tree. Implements {@link Iterable} allowing the type to be used
 * in range-based for-loops.
 *
 * @param <_Ty> the type to store in the tree
 *
 * @see Iterable
 * @see Comparable
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 06/03/25
 */
public class BinarySearchTree <_Ty extends Comparable<_Ty>> implements Iterable<BinarySearchTree<_Ty>.Node>
{
    /**
     * Represents a node in the {@link BinarySearchTree}. Contains a {@code value}, and pointers to the
     * {@code left} and {@code right} nodes below this one in the tree.
     */
    public class Node
    {
        /**
         * Create a new node with the given {@code value}.
         *
         * @param value the value to assign this {@link Node} with
         */
        public Node(_Ty value)
        {
            this.Value = value;
            this.Left = null;
            this.Right = null;
        }

        /** The value of this node. */
        public _Ty Value;

        /** The pointer to the node left of this one. */
        public Node Left;

        /** The pointer to the node right of this one. */
        public Node Right;
    }

    /**
     * Performs an Inorder traversal over the {@link BinarySearchTree} allowing the type to be used in
     * range-based for-loops.
     *
     * @see Iterator
     */
    public class BSTIterator implements Iterator<Node>
    {
        /**
         * Construct a new {@link BSTIterator}.
         *
         * @param root the root node to traverse from
         */
        public BSTIterator(Node root)
        {
            m_NodeStack = new Stack<Node>();
            PushLeft(root);
        }

        /**
         * Does the iterator have another node?
         */
        @Override
        public boolean hasNext()
        {
            return !m_NodeStack.isEmpty();
        }

        /**
         * Get the next node.
         */
        @Override
        public Node next()
        {
            Node node = m_NodeStack.pop();
            PushLeft(node.Right);

            return node;
        }

        // Push node onto the node stack for inorder traversal
        private void PushLeft(Node node)
        {
            while (node != null)
            {
                m_NodeStack.push(node);
                node = node.Left;
            }
        }

        // Stack of nodes to be used for inorder traversal
        private Stack<Node> m_NodeStack;
    }

    /**
     * Default constructor.
     */
    public BinarySearchTree()
    {
        m_Root = null;
    }

    /**
     * Insert a new {@code value} into the tree. Creates a new {@link Node}.
     *
     * @param value the value to insert
     */
    public void Insert(_Ty value)
    {
        m_Root = InsertValueRootedAt(m_Root, value);
    }

    /**
     * Find a {@code value} in the tree.
     *
     * @param value the value to search for
     * @return the {@link Node} at which the {@code value} was found at
     */
    public Node Find(_Ty value)
    {
        return FindNodeWithValue(m_Root, value);
    }

    /**
     * Is this tree empty?
     *
     * @return {@code true} if this tree is empty, {@code false} otherwise
     */
    public boolean Empty()
    {
        return m_Root == null;
    }

    /**
     * Get the {@link Iterator} to this tree.
     */
    @Override
    public Iterator<Node> iterator()
    {
        return new BSTIterator(m_Root);
    }

    /**
     * Get the root {@link Node} of this tree.
     *
     * @return the root {@link Node} of this tree
     */
    public Node GetRoot() { return m_Root; }

    // Recursively insert value into the tree
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

    // Recursively find value in the tree
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

    // The root node of this tree
    private Node m_Root;
}
