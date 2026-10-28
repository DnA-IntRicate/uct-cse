/**
 * Simple hash table implementation using quadratic probing.
 *
 * @author Stephan Jamieson
 * @author Adam Foflonker (FFLADA001)
 * @version 12/04/25
 */
public class QPHashTable  extends HashTable {


    /**
     * Create an QPHashTable with DEFAULT_SIZE table.
     */
    public QPHashTable() { super(); }

    /**
     * Create an QPHashTable with the given default size table.
     */
    public QPHashTable(final int size) { super(size); }

    /**
     * Find the index for entry: if entry is in the table, then returns its position;
     * if it is not in the table then returns the index of the first free slot.
     * Returns -1 if a slot is not found (such as when the table is full under LP).
     */
    protected int findIndex(String key)
    {
        int start = hashFunction(key);  // This hash function already mods with table size
        for (int i = 0; i < tableSize(); ++i)
        {
            int cursor = (start + (i * i)) % tableSize();
            incProbeCount();

            if (table[cursor] == null)
                return cursor;

            if (table[cursor].equals(key))
                return cursor;
        }

        return -1;
    }
}
