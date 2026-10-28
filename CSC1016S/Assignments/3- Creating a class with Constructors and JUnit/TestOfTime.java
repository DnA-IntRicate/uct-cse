// Adam Foflonker
// FFLADA001
// 7 August 2024
// Unit test for the 'Time' and 'Duration' classes using JUnit

import static org.junit.Assert.*;
import org.junit.Test;


public class TestOfTime
{
    // Check that a Time object does actually store the time value provided as a parameter during creation (by calling toString).
    @Test
    public void Test1()
    {
        final String TEST_VALUE = "12:00:00";

        Time t = new Time(TEST_VALUE);
        assertEquals(t.toString(), TEST_VALUE);
    }

    // Check that subtracting an earlier Time from a later Time produces a Duration of the correct length.
    @Test
    public void Test2()
    {
        Time t1 = new Time(5, 0, 0);
        Time t2 = new Time(6, 0, 0);
        assertEquals(t2.subtract(t1), new Duration(TimeUnit.HOUR, 1));
    }

    // Check that subtracting a Time from itself produces a zero Duration.
    @Test
    public void Test3()
    {
        Time t = new Time(9, 30, 0);
        assertEquals(t.subtract(t), new Duration(0));
    }

    // Check that the 'intValue' method works with a parameter of "millisecond"
    @Test
    public void Test4()
    {
        final long TEST_VALUE = 1000;

        Duration d = new Duration(TEST_VALUE);
        assertEquals(d.intValue("millisecond"), TEST_VALUE);
    }

    // Check that the 'intValue' method works with a parameter of "second"
    @Test
    public void Test5()
    {
        final long TEST_VALUE = 1000;
        final long EXPECTED_VALUE = 1;

        Duration d = new Duration(TEST_VALUE);
        assertEquals(d.intValue("second"), EXPECTED_VALUE);
    }

    // Check that the 'intValue' method works with a parameter of "minute"
    @Test
    public void Test6()
    {
        final long TEST_VALUE = 60;
        final long EXPECTED_VALUE = 1;

        Duration d = new Duration(TimeUnit.SECOND, TEST_VALUE);
        assertEquals(d.intValue("minute"), EXPECTED_VALUE);
    }

    // Check that the 'intValue' method works with a parameter of "hour"
    @Test
    public void Test7()
    {
        final long TEST_VALUE = 60;
        final long EXPECTED_VALUE = 1;

        Duration d = new Duration(TimeUnit.MINUTE, TEST_VALUE);
        assertEquals(d.intValue("hour"), EXPECTED_VALUE);
    }
}
