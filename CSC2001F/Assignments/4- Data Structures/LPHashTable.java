/**
 * Simple hash table implementation using linear probing.
 *
 * @author Stephan Jamieson
 * @author Adam Foflonker (FFLADA001)
 * @version 12/04/25
 */
public class LPHashTable extends HashTable {

    /**
     * Create an LPHashTable with DEFAULT_SIZE table.
     */
    public LPHashTable() { super(); }

    /**
     * Create an LPHashTable with the given default size table.
     */
    public LPHashTable(final int size) { super(size); }

    /**
     * Find the index for entry: if entry is in the table, then returns its position;
     * if it is not in the table then returns the index of the first free slot.
     * Returns -1 if a slot is not found (such as when the table is full under LP).
     */
    protected int findIndex(String key)
    {
        int cursor = hashFunction(key);  // This hash function already mods with table size
        for (int i = 0; i < tableSize(); ++i)
        {
            incProbeCount();

            if (table[cursor] == null)
                return cursor;

            if (table[cursor].equals(key))
                return cursor;

            cursor = (cursor + 1) % tableSize();
        }

        return -1;
    }
}
