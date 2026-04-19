import java.util.Scanner;
import java.util.Queue;
import java.util.LinkedList;


public class FIFO
{
    private static int firstInFirstOut(final Memory frames, final Integer[] pageReferences)
    {
        int pageFaults = 0;
        Queue<Integer> pageQueue = new LinkedList<Integer>(); // FIFO Queue

        for (int page : pageReferences)
        {
            // Handle page hit
            if (frames.contains(page))
            {
                System.out.printf("%d: -\n", page);
                continue;
            }

            pageFaults++;

            // Insert page in the first empty frame
            boolean inserted = false;
            for (int frame = 0; frame < frames.size(); ++frame)
            {
                if (frames.isEmpty(frame))
                {
                    frames.put(frame, page);
                    pageQueue.add(page);
                    inserted = true;

                    System.out.printf("%d: %s\n", page, frames);
                    break;
                }
            }

            // If no empty frame is found, perform the FIFO page replacement
            if (!inserted)
            {
                frames.replace(pageQueue.remove(), page);
                pageQueue.add(page);

                System.out.printf("%d: %s\n", page, frames);
            }
        }

        return pageFaults;
    }

    public static void main(final String[] args)
    {
        try (Scanner stdIn = new Scanner(System.in))
        {
            System.out.println("Enter the physical memory size (number of frames):");
            final int numFrames = stdIn.nextInt();
            stdIn.nextLine();

            System.out.println("Enter the string of page references:");
            final String referenceString = stdIn.nextLine();

            System.out.printf("Page faults: %d.\n", firstInFirstOut(new Memory(numFrames), toArray(referenceString)));
        }
    }

    private static Integer[] toArray(final String referenceString)
    {
        final Integer[] result = new Integer[referenceString.length()];
        for(int i = 0; i < referenceString.length(); ++i)
            result[i] = Character.digit(referenceString.charAt(i), 10);

        return result;
    }
}
