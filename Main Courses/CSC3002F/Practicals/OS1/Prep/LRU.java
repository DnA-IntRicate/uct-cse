import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;


public class LRU
{
    private static int leastRecentlyUsed(final Memory frames, final Integer[] pageReferences)
    {
        int pageFaults = 0;

        // Maps a page reference to the number of cycles since that page reference was last used
        Map<Integer, Integer> lruMap = new HashMap<Integer, Integer>();
        int time = 0;

        for (int page : pageReferences)
        {
            time++;

            // Handle page hit
            if (frames.contains(page))
            {
                lruMap.put(page, time);
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
                    lruMap.put(page, time);
                    inserted = true;

                    System.out.printf("%d: %s\n", page, frames);
                    break;
                }
            }

            // If no empty frame is found, perform the LRU page replacement
            if (!inserted)
            {
                // LRU: Evict the page that hasn't been used for the longest time

                int lruPage = -1;
                int oldestTime = Integer.MAX_VALUE;
                for (int usedPage : frames.pages())
                {
                    if (lruMap.get(usedPage) < oldestTime)
                    {
                        oldestTime = lruMap.get(usedPage);
                        lruPage = usedPage;
                    }
                }

                // Swap the pages and update tracking
                frames.replace(lruPage, page);
                lruMap.remove(lruPage);
                lruMap.put(page, time);

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

            System.out.printf("Page faults: %d.\n", leastRecentlyUsed(new Memory(numFrames), toArray(referenceString)));
        }
    }

    private static Integer[] toArray(final String referenceString)
    {
        final Integer[] result = new Integer[referenceString.length()];
        for (int i = 0; i < referenceString.length(); ++i)
            result[i] = Character.digit(referenceString.charAt(i), 10);

        return result;
    }
}
