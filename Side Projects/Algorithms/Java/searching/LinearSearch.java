package searching;

import java.util.Arrays;
import java.util.Scanner;


public class LinearSearch
{
    public static int Search(int begin, int end, int[] arr, int x)
    {
        if (begin > end)
            return -1;

        for (int i = begin; i <= end; ++i)
        {
            if (arr[i] == x)
                return i;
        }

        return -1;
    }

    public static void main(String[] args)
    {
        System.out.println("--------------------------------------------------------------");
        System.out.println("Linear Search");
        System.out.println("--------------------------------------------------------------");

        int[] arr = { 2, 4, 5, 8, 99, 34, 5, 42, 56, 0, 88, 12, 45 };
        System.out.println("List: " + Arrays.toString(arr));

        System.out.print("Enter a number to search for: ");
        Scanner scanner = new Scanner(System.in);
        int num = Integer.parseInt(scanner.nextLine());
        scanner.close();

        int searchedIdx = LinearSearch.Search(0, arr.length - 1, arr, num);
        System.out.printf("Index of %d in list: %d\n", num, searchedIdx);
    }
}
