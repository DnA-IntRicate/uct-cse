import java.util.Iterator;

/**
 * Iterable, generic linked list implementation for data structures class.
 * @author Bhavana Harrilal
 * @param <T> the type of values stored in the list
 */

@SuppressWarnings("hiding")
public class SimpleLinkedList<T> implements Iterable<T> {
    private class Node<T> {
        private T value;
        private Node<T> next;

        public Node(T data) {
            this.value = data;
        }

        public boolean hasNext() {
            return this.next != null;
        }
    }

    private class NodeIterator<T> implements Iterator<T> {
        private Node<T> current;

        public NodeIterator(Node<T> start) {
            this.current = start;
        }

        @Override
        public boolean hasNext() {
            return current != null;
        }

        @Override
        public T next() {
            T value = current.value;
            current = current.next;
            return value;
        }

        @Override
        public void remove() {
        }
    }

    private Node<T> head;
    private int numNodes = 0;

    public SimpleLinkedList() {
        this.head = null;
    }

    public SimpleLinkedList(T[] objects) {
        this.addAll(objects);
    }

    @Override
    /**
     * @see java.util.Iterable#iterator()
         */
    public Iterator<T> iterator() {
        return new NodeIterator<T>(this.head);
    }

    /**
     * Retrieves the size of the SimpleLinkedList
     * @return size of the SimpleLinkedList
     */
    public int size() {
        return numNodes;
    }

    /**
     * Adds the data to the end of the list.
     * @param data the data to append
     */
    public void add(T data) {
        if (this.head == null) {
            this.head = new Node<T>(data);
        }
        else {
            this.getTail().next = new Node<T>(data);
        }

        this.numNodes++;
    }

    /**
     * Adds the data to the end of the list.
     * @param data the data to append
     */
    public void addAll(T[] data) {
        for (T datum : data) {
            this.add(datum);
        }
    }

    /**
     * Gets the last element of the list.
     * @return Node<T> representing last element
     */
    private Node<T> getTail() {
        Node<T> current = this.head;
        while (current.hasNext()) {
            current = current.next;
        }
        return current;
    }

    /**
     * Get returns the element at the specified index.
     * @param index the element to retrieve
     * @return the value of the element
     */
    public T get(int index) {
        return this.getNode(index).value;
    }

    /**
     * Private helper to get the actual Node representation at an index
     * @param index the index to find
     * @return the internal Node representation
     */
    private Node<T> getNode(int index) {
        Node<T> current = this.head;
        for (int i = 0; i < this.size(); i++) {
            if (i == index) {
                return current;
            }

            current = current.next;
        }

        return null;
    }


    /**
     * Changes the value of the specified index to the given value.
     * @param index the index to retrieve
     * @param value the value to update
     */
    public void set(int index, T value) {
        this.getNode(index).value = value;
    }

    /**
     * returns the first index containing the given value
     * @param value value to search for
     * @return index of the first instance of value
     */
    public int indexOf(T value) {
        int index = 0;
        for (T object : this) {
            if (object == value)
                return index;
            index ++;
        }

        return -1;
    }

    /**
     * Inserts the given value at the index, moves all subsequent elements down 1.
     * @param index the index at which to insert
     * @param item the item to insert
     */
    public void insert(int index, T item) {
        if (index == this.size()) {
            this.add(item);
        } else {
            Node<T> newNode = new Node<T>(item);
            newNode.next = this.getNode(index);
            if (index == 0) {
                this.head = newNode;
            } else {
                this.getNode(index - 1).next = newNode;
            }

            this.numNodes++;
        }
    }

    /**
     * Removes the element at the given index, moves all subsequent elements up 1.
     * @param index the index at which to remove
     */
    public void removeAt(int index) {
        if (index == 0) {
            this.head = this.getNode(1);
        } else {
            Node<T> prev = this.getNode(index-1);
            // memory efficiency, since this is singly linked
            prev.next = prev.next.next;
        }

        this.numNodes--;
    }

    /**
     * Removes the first occurrence of the given value, moves all subsequent elements up 1.
     * @param value the value to search for
     */
    public void remove(T value) {
        this.removeAt(this.indexOf(value));
    }

    /**
     * Truncates the SimpleLinkedList at the specified size.
     * @param size the new size of the SimpleLinkedList
     */
    public void trimToSize(int size) {
        if (size == 0) {
            this.head = null;
        } else {
            this.getNode(size-1).next = null;
        }
        this.numNodes = size;
    }
}
