/**
 * A basic implementation of an AVL tree using a {@code key}-{@code value} system.
 *
 * @param <_KTy> the type of the keys in the tree. Each key references a value/data stored at that node in the tree
 * @param <_Ty> the type of the values/data referenced by each key in the tree.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 22/03/25
 */
public class AVLTree <_KTy extends Comparable<_KTy>, _Ty>
{
    /**
     * Represents a node in the {@link AVLTree}. Contains a {@code key}, {@code value}, pointers to the
     * {@code left} and {@code right} nodes below this one in the tree, and the {@code height} of the node.
     */
    public class Node
    {
        /**
         * Create a new node with the given {@code key} and {@code value}.
         *
         * @param key the searchable key of this node in the tree
         * @param value the value to assign this {@link Node} with
         */
        public Node(_KTy key, _Ty value)
        {
            this.Key = key;
            this.Value = value;
            this.Height = 1;
            this.Left = null;
            this.Right = null;
        }

        /** The key of this node. */
        public _KTy Key;

        /** The value of this node. */
        public _Ty Value;

        /** The height of this node. */
        public int Height;

        /** The pointer to the node left of this one. */
        public Node Left;

        /** The pointer to the node right of this one. */
        public Node Right;
    }

    /**
     * Default constructor.
     */
    public AVLTree()
    {
        m_Root = null;
    }

    /**
     * Insert a new {@code value} into the tree attached to the given {@code key}. Creates a new {@link Node}.
     *
     * @param key the key of the value in the tree
     * @param value the value to insert
     */
    public void Insert(_KTy key, _Ty value)
    {
        m_Root = InsertValueRootedAt(m_Root, key, value);
    }

    /**
     * Find a {@code key} in the tree.
     *
     * @param key the key to search for
     * @return the {@link Node} at which the {@code key} was found at
     */
    public Node Find(_KTy key)
    {
        return FindNodeWithKey(m_Root, key);
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
     * Get the root {@link Node} of this tree.
     *
     * @return the root {@link Node} of this tree
     */
    public Node GetRoot() { return m_Root; }

    // Recursively insert into the tree
    private Node InsertValueRootedAt(Node root, _KTy key, _Ty value)
    {
        if (root == null)
            return new Node(key, value);

        InstrumentationCounter.IncrementInserts();

        if (key.compareTo(root.Key) < 0)
            root.Left = InsertValueRootedAt(root.Left, key, value);
        else
        {
            InstrumentationCounter.IncrementInserts();

            if (key.compareTo(root.Key) > 0)
                root.Right = InsertValueRootedAt(root.Right, key, value);
            else
                return root;    // Disallow duplicate keys in the tree
        }

        root.Height = Math.max(Height(root.Left), Height(root.Right)) + 1;
        int balance = Balance(root);

        if (balance > 1)
        {
            // Left Heavy (LL)
            InstrumentationCounter.IncrementInserts();
            if (key.compareTo(root.Left.Key) < 0)
                return RightRotate(root);

            // Left-Right Heavy (LR)
            InstrumentationCounter.IncrementInserts();
            if (key.compareTo(root.Left.Key) > 0)
            {
                root.Left = LeftRotate(root.Left);
                return RightRotate(root);
            }
        }

        if (balance < -1)
        {
            // Right Heavy (RR)
            InstrumentationCounter.IncrementInserts();
            if (key.compareTo(root.Right.Key) > 0)
                return LeftRotate(root);

            // Right-Left Heavy (RL)
            InstrumentationCounter.IncrementInserts();
            if (key.compareTo(root.Right.Key) < 0)
            {
                root.Right = RightRotate(root.Right);
                return LeftRotate(root);
            }
        }

        return root;
    }

    // Recursively find key in the tree
    private Node FindNodeWithKey(Node root, _KTy key)
    {
        if (root == null)
            return null;

        InstrumentationCounter.IncrementSearches();

        if (key.equals(root.Key))
            return root;

        if (key.compareTo(root.Key) < 0)
            return FindNodeWithKey(root.Left, key);

        return FindNodeWithKey(root.Right, key);
    }

    // Returns the height of the given node
    private int Height(final Node node) { return (node == null) ? 0 : node.Height; }

    // Returns the balancing factor of the given node
    private int Balance(final Node node) { return (node == null) ? 0 : Height(node.Left) - Height(node.Right); }

    // Rotates the given node to the right
    private Node RightRotate(Node node)
    {
        Node l = node.Left;
        Node temp = l.Right;

        l.Right = node;
        node.Left = temp;

        node.Height = Math.max(Height(node.Left), Height(node.Right)) + 1;
        l.Height = Math.max(Height(l.Left), Height(l.Right)) + 1;

        return l;
    }

    // Rotates the given node to the left
    private Node LeftRotate(Node node)
    {
        Node r = node.Right;
        Node temp = r.Left;

        r.Left = node;
        node.Right = temp;

        node.Height = Math.max(Height(node.Left), Height(node.Right)) + 1;
        r.Height = Math.max(Height(r.Left), Height(r.Right)) + 1;

        return r;
    }

    // The root node of this tree
    private Node m_Root;
}
