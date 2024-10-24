/**
 * A basic LIFO stack.
 *
 * @param <_Ty> The type to store in the stack
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 24/10/24
 *
 * @implNote This implementation is primarily just a wrapper-class around {@link Vector}.
 */
public class Stack<_Ty>
{
    /**
     * Default constructor. Creates a new empty {@link Stack}.
     */
    public Stack()
    {
        m_Data = new Vector<_Ty>();
    }

    /**
     * Pushes the element {@code value} onto the top of this stack.
     *
     * @param value the element to push onto the top
     */
    public void Push(final _Ty value) { m_Data.PushBack(value); }

    /**
     * Pops the element at the top of this stack and returns it.
     *
     * @return the popped element
     */
    public _Ty Pop() { return m_Data.PopBack(); }

    /**
     * Returns the element at the top of this stack.
     *
     * @return the element at the top of this stack
     */
    public _Ty Top() { return m_Data.Back(); }

    /**
     * Checks if this stack is empty.
     *
     * @return {@code true} if this stack is empty, {@code false} otherwise
     */
    public boolean Empty() { return m_Data.Empty(); }

    /** The internal data container. */
    private Vector<_Ty> m_Data;
}
