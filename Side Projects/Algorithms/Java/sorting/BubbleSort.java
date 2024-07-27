package sorting;

import java.util.Arrays;


public class BubbleSort
{
    public static int[] Sort(int[] arr)
    {
        if (arr.length == 0)
            return new int[0];

        int[] res = arr;
        for (int i = 0; i < res.length; ++i)
        {
            for (int j = 0; j < res.length - i - 1; ++j)
            {
                if (res[j] > res[j + 1])
                {
                    int swp = res[j];
                    res[j] = res[j + 1];
                    res[j + 1] = swp;
                }
            }
        }

        return res;
    }

    public static void main(String[] args)
    {
        System.out.println("--------------------------------------------------------------");
        System.out.println("Bubble Sort");
        System.out.println("--------------------------------------------------------------");

        int[] arr = { 38, 27, 43, 10, 1, 38 };
        System.out.println(Arrays.toString(BubbleSort.Sort(arr)));
    }
}
