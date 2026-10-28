// Adam Foflonker
// CSC1016S-2026 Practical Test 1P Test code
// 03 Sept 2026


public class TestNumberBuffer
{
    public static void main(String[] args)
    {
        NumberBuffer numBuf = new NumberBuffer('|');
        numBuf.addNumbers("3|54"); numBuf.addNumbers("17|14|9|");

        System.out.printf("%s %s\n", numBuf.nextNumber(), numBuf.nextNumber());
        System.out.printf("%s %s\n", numBuf.nextNumber(), numBuf.nextNumber());

        // The output will be "3 54" then "17 14".
    }
}
