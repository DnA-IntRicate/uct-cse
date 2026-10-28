import static org.junit.Assert.*;
import org.junit.Test;

/**
 * A Junit unit test for {@link SimpleLinkedList}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 24/10/24
 */
public class SimpleLinkedListTest
{
    /**
     * Checks that a linked list created using the constructor (with a list of items passed in as a parameter)
     * contains the items passed in.
     */
    @Test
    public void Test1()
    {
        final Integer[] NUMBERS = { 1, 2, 3, 4, 5, 6 };
        final SimpleLinkedList<Integer> LST = new SimpleLinkedList<Integer>(NUMBERS);

        for (int i = 0; i < LST.size(); ++i)
            assertEquals(LST.get(i), NUMBERS[i]);
    }

    /**
     * Checks that indexOf applied to search through a linked list of items returns the correct index
     * for each item in the list.
     */
    @Test
    public void Test2()
    {
        final Integer[] NUMBERS = { 1, 2, 3, 4, 5, 6 };
        final SimpleLinkedList<Integer> LST = new SimpleLinkedList<Integer>(NUMBERS);

        for (int i = 0; i < NUMBERS.length; ++i)
            assertEquals(LST.indexOf(NUMBERS[i]), i);
    }

    /**
     * Checks that the insertion of an item in a linked list of items using insert results in the item being
     * inserted and appearing in the correct position.
     */
    @Test
    public void Test3()
    {
        final Integer[] NUMBERS = { 1, 2, 3, 4, 5, 6 };
        final int TEST_NUM = 7;
        final int TEST_INDEX = 4;

        SimpleLinkedList<Integer> lst = new SimpleLinkedList<Integer>(NUMBERS);
        lst.insert(TEST_INDEX, TEST_NUM);
        assertEquals(lst.indexOf(TEST_NUM), TEST_INDEX);
    }

    /**
     * Check that trimToSize does truncate the list to the size specified.
     */
    @Test
    public void Test4()
    {
        final Integer[] NUMBERS = { 1, 2, 3, 4, 5, 6 };

        SimpleLinkedList<Integer> lst = new SimpleLinkedList<Integer>(NUMBERS);
        lst.trimToSize(lst.size() - 1);
        assertEquals(lst.size(), NUMBERS.length - 1);
    }
}
