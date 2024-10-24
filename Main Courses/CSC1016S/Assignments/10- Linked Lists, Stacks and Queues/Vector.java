import java.util.Arrays;
import java.util.Iterator;
import java.util.Objects;

/**
 * A dynamic array-like container class that provides various methods for managing and manipulating elements.
 * This implmentation was created to mimic that of std::vector in the C++ Standard Template Library and was inspired
 * by 'DnA-IntRicate/Powerhouse.'
 *
 * @param <_Ty> The type to store in the vector
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 24/10/24
 *
 * @see std::vector: "https://cplusplus.com/reference/vector/vector"
 * @see DnA-IntRicate/Powerhouse: "https://github.com/DnA-IntRicate/Powerhouse/blob/master/Source/Powerhouse/Powerhouse.Vector.pas"
 */
@SuppressWarnings("unchecked")
public class Vector<_Ty> implements Iterable<_Ty>
{
    /**
     * Creates a new {@link Vector} with the given initial {@code capacity}.
     *
     * @param capacity the initial capacity of the vector
     */
    public Vector(int capacity)
    {
        m_Data = ArrayResize(m_Data, capacity);
        m_Size = 0;
    }

    /**
     * Creates a new {@link Vector} with the given varargs.
     *
     * @param values the elements to initialize the vector with
     */
    @SafeVarargs
    public Vector(final _Ty... values)
    {
        m_Data = values;
        m_Size = m_Data.length;
    }

    /**
     * Copy constructor.
     *
     * @param other the {@link Vector} to copy from
     */
    public Vector(final Vector<_Ty> other)
    {
        m_Data = ArrayResize(other.m_Data, other.m_Data.length);
        m_Size = other.m_Size;
    }

    /**
     * Default constructor. Creates a new empty {@link Vector}.
     */
    public Vector()
    {
        this(0);
    }

    /**
     * Appends the given element {@code value} to the end of this vector.
     *
     * @param value the element to append to the end of this vector
     */
    public void PushBack(final _Ty value)
    {
        if (Size() == GetCapacity())
            Grow();

        m_Data[m_Size++] = value;
    }

    /**
     * Removes the last element from this vector and returns it.
     *
     * @return the last element of this vector that was popped
     */
    public _Ty PopBack()
    {
        if (!Empty())
        {
            _Ty res = m_Data[--m_Size];
            m_Data[m_Size] = null;

            return res;
        }

        return null;
    }

    /**
     * Inserts the given element {@code value} at the specified {@code index} into this vector.
     *
     * @param index the index at which to insert the element {@code value}
     * @param value the element to insert
     */
    public void Insert(int index, final _Ty value)
    {
        AssertIndex(index);

        if (GetCapacity() < (m_Size + 1))
            SetCapacity(m_Size + 1);

        if (index < m_Size)
            System.arraycopy(m_Data, index, m_Data, index + 1, m_Size - index);

        m_Data[index] = value;
        m_Size++;
    }

    /**
     * Removes the element at the given {@code index}.
     *
     * @param index the index of the element to remove
     */
    public void Erase(int index)
    {
        AssertIndex(index);

        if (index < (m_Size - 1))
            System.arraycopy(m_Data, index + 1, m_Data, index, m_Size - index - 1);

        m_Data[--m_Size] = null;
    }

    /**
     * Resizes this vector to the given {@code newSize}.
     *
     * @param newSize the new size of the vector
     */
    public void Resize(int newSize)
    {
        if (newSize > Size())
        {
            if (newSize > GetCapacity())
                SetCapacity(newSize);

            while (Size() < newSize)
                m_Data[m_Size++] = null;
        }
        else if (newSize < Size())
        {
            while (Size() > newSize)
                m_Data[--m_Size] = null;
        }

        SetCapacity(newSize);
    }

    /**
     * Reserves space for this vector to accommodate the given {@code newCapacity}.
     *
     * @param newCapacity the new capacity to reserve
     */
    public void Reserve(int newCapacity)
    {
        if (newCapacity > GetCapacity())
            SetCapacity(newCapacity);
    }

    /**
     * Reduces the capacity of this vector to fit its current size.
     */
    public void ShrinkToFit()
    {
        if (Size() < GetCapacity())
            SetCapacity(Size());
    }

    /**
     * Removes all elements from this vector.
     */
    public void Clear()
    {
        while (!Empty())
            PopBack();
    }

    /**
     * Finds the index of the given {@code value} in this vector. Returns {@code -1} if it was not found.
     *
     * @param value the value to search for
     * @return the index of {@code value} in this vector or {@code -1} if it was not found
     */
    public int Find(final _Ty value)
    {
        for (int i = 0; i < Size(); ++i)
        {
            if (Objects.equals(value, m_Data[i]))
                return i;
        }

        return -1;
    }

    /**
     * Checks if this vector contains the given {@code value}.
     *
     * @param value the element to search for
     * @return {@code true} if this vector contains {@code value}, {@code false} otherwise
     */
    public boolean Contains(final _Ty value)
    {
        return Find(value) != -1;
    }

    /**
     * Checks if this vector is equal to {@code other}.
     *
     * @param other the vector to check for equality
     * @return {@code true} if this vector equals {@code other}, {@code false} otherwise
     */
    public boolean Equals(final Vector<_Ty> other)
    {
        return m_Data.equals(other.m_Data) && (m_Size == other.m_Size);
    }

    /**
     * Checks if this vector is empty.
     *
     * @return {@code true} if this vector is empty, {@code false} otherwise
     */
    public boolean Empty() { return Size() == 0; }

    /**
     * Returns the size of this vector.
     *
     * @return the size of this vector
     */
    public int Size() { return m_Size; }

    /**
     * Returns the capacity of this vector.
     *
     * @return the capacity of this vector
     */
    public int Capacity() { return GetCapacity(); }

    /**
     * Returns a reference to the internal data array of this vector.
     *
     * @return a reference to the internal data array of this vector
     */
    public _Ty[] Data() { return m_Data; }

    /**
     * Returns the first element of this vector.
     *
     * @return the first element of this vector
     */
    public _Ty Front() { return m_Data[First()]; }

    /**
     * Returns the last element of this vector.
     *
     * @return the last element of this vector
     */
    public _Ty Back() { return m_Data[Last()]; }

    /**
     * Returns the first valid index of this vector. Always returns 0.
     *
     * @return 0
     */
    public int First() { return 0; }

    /**
     * Returns the last valid index of this vector.
     *
     * @return the last valid index of this vector
     */
    public int Last() { return m_Size - 1; }


    /**
     * Returns the element at the given {@code index}.
     *
     * @param index the index of the element to retrieve
     * @return the element at the given {@code index}
     */
    public _Ty At(int index)
    {
        AssertIndex(index);
        return m_Data[index];
    }

    /**
     * Sets the element at the given {@code index} to the given {@code value}.
     */
    public void SetAt(int index, final _Ty value)
    {
        AssertIndex(index);
        m_Data[index] = value;
    }

    /** Iterator to this vector. */
    private class VectorIterator implements Iterator<_Ty>
    {
        @Override
        public boolean hasNext() { return m_Index < m_Size; }

        @Override
        public _Ty next()
        {
            if (!hasNext())
                throw new IndexOutOfBoundsException("No more elements left!");

            return m_Data[m_Index++];
        }

        private int m_Index = 0;
    }

    /**
     * Returns an {@link Iterator} to this vector that can be used in range-based for-loops.
     *
     * @return an {@link Iterator} to this vector
     */
    @Override
    public Iterator<_Ty> iterator()
    {
        return new VectorIterator();
    }

    /** Get capacity of this vector. */
    private int GetCapacity() { return m_Data.length; }

    /** Set the capacity of this vector. */
    private void SetCapacity(int newCapacity)
    {
        if (newCapacity != GetCapacity())
        {
            m_Data = ArrayResize(m_Data, newCapacity);
            m_Size = Math.min(m_Size, newCapacity);
        }
    }

    /** Resize or initialize an array. */
    private _Ty[] ArrayResize(_Ty[] arr, int newSize)
    {
        if (arr == null)
            return (_Ty[])(new Object[newSize]);

        return Arrays.copyOf(arr, newSize);
    }

    /**
     * Grow the size of this vector's internal array. If the capacity is less than 64, then it is doubled. Otherwise the
     * capacity is increased by 25%.
     */
    private void Grow()
    {
        int newCapacity = 0;
        if (GetCapacity() == 0)
            newCapacity = 1;
        else if (GetCapacity() < 64)
            newCapacity = GetCapacity() * 2;
        else
            newCapacity = GetCapacity() + (GetCapacity() / 4);

        SetCapacity(newCapacity);
    }

    /** Asserts if the index is valid. */
    private void AssertIndex(int index)
    {
        if ((index < 0) || (index > m_Size))
            throw new IndexOutOfBoundsException("Index out of bounds: " + index);
    }

    /** The internal data array of this vector. */
    private _Ty[] m_Data;

    /**
     * The size of this vector. This number represents how many elements are present in this vector, not the capacity
     * of it. The capacity of the vector is the length of the array m_Data.
     */
    private int m_Size;
}
