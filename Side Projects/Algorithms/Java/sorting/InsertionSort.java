package sorting;

import java.util.Arrays;


public class InsertionSort
{
    public static int[] Sort(int[] arr)
    {
        if (arr.length == 0)
            return new int[0];

        int[] res = arr;
        for (int i = 1; i < res.length; ++i)
        {
            int key = res[i];

            int j = i - 1;
            while ((j >= 0) && (key < res[j]))
            {
                res[j + 1] = res[j];
                j -= 1;
            }

            res[j + 1] = key;
        }

        return res;
    }

    public static void main(String[] args)
    {
        System.out.println("--------------------------------------------------------------");
        System.out.println("Insertion Sort");
        System.out.println("--------------------------------------------------------------");

        int[] arr = { 38, 27, 43, 10, 1, 38 };
        System.out.println(Arrays.toString(InsertionSort.Sort(arr)));
    }
}
