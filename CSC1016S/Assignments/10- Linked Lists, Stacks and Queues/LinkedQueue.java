/**
 * A basic FIFO queue implemented using a single linked list.
 *
 * @param <_Ty> The type to store in the linked queue
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 24/10/24
 */
public class LinkedQueue<_Ty>
{
    /**
     * Default constructor. Creates an empty {@link LinkedQueue}.
     */
    public LinkedQueue()
    {
        m_Front = null;
        m_Back = null;
        m_Size = 0;
    }

    /**
     * Adds the element {@code value} onto the end of this queue.
     *
     * @param value the element to enqueue
     */
    public void Enqueue(final _Ty value)
    {
        Node newNode = new Node(value);
        if (Empty())
            m_Front = newNode;
        else
            m_Back.Next = newNode;

        m_Back = newNode;
        ++m_Size;
    }

    /**
     * Removes the first element in the queue.
     *
     * @return the dequeued element
     */
    public _Ty Dequeue()
    {
        if (Empty())
            return null;

        _Ty data = m_Front.Data;
        m_Front = m_Front.Next;

        if (m_Front == null)
            m_Back = null;

        --m_Size;
        return data;
    }

    /**
     * Checks if this queue is empty.
     *
     * @return {@code true} if this queue is empty, {@code false} otherwise
     */
    public boolean Empty() { return (m_Front == null) || (m_Size == 0); }

    /** Represents a node in the underlying linked list data structure. */
    private class Node
    {
        /** The data of this node. */
        public _Ty Data;

        /** The next node this one is linked to. */
        public Node Next;

        /** Create a new node with the given data. */
        public Node(final _Ty data)
        {
            Data = data;
            Next = null;
        }
    }

    /** The front of this queue. */
    private Node m_Front;

    /** The back of this queue. */
    private Node m_Back;

    /** The size of this queue. */
    private int m_Size;
}
