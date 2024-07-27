package searching;

import sorting.BubbleSort;
import java.util.Arrays;
import java.util.Scanner;


public class BinarySearch
{
    public static int Search(int begin, int end, int[] arr, int x)
    {
        if (begin > end)
            return -1;

        int mid = (begin + end) / 2;
        if (arr[mid] == x)
            return mid;

        if (arr[mid] < x)
            return Search(mid + 1, end, arr, x);

        return Search(begin, mid - 1, arr, x);
    }

    public static void main(String[] args)
    {
        System.out.println("--------------------------------------------------------------");
        System.out.println("Binary Search");
        System.out.println("--------------------------------------------------------------");

        int[] arr = { 2, 4, 5, 8, 99, 34, 5, 42, 56, 0, 88, 12, 45 };
        System.out.println("List: " + Arrays.toString(arr));

        arr = BubbleSort.Sort(arr);
        System.out.println("Bubble sorted: " + Arrays.toString(arr));

        System.out.print("Enter a number to search for: ");
        Scanner scanner = new Scanner(System.in);
        int num = Integer.parseInt(scanner.nextLine());
        scanner.close();

        int searchedIdx = BinarySearch.Search(0, arr.length, arr, num);
        System.out.printf("Index of %d in list: %d\n", num, searchedIdx);
    }
}
