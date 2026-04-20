import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;


public class OPT
{
    private static int optimal(final Memory frames, final Integer[] pageReferences)
    {
        int pageFaults = 0;
        for (int i = 0; i < pageReferences.length; ++i)
        {
            int page = pageReferences[i];

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
                    inserted = true;

                    System.out.printf("%d: %s\n", page, frames);
                    break;
                }
            }

            // If no empty frame is found, perform the OPT page replacement
            if (!inserted)
            {
                // OPT: Evict the page that won't be used for the longest time in the future

                // Maps a page reference to the number of cycles before it'll be used next
                Map<Integer, Integer> pageDistanceMap = new HashMap<Integer, Integer>();
                for (int usedPage : frames.pages())
                {
                    int distance = 0;
                    boolean found = false;

                    for (int j = i + 1; j < pageReferences.length; ++j)
                    {
                        if (usedPage == pageReferences[j])
                        {
                            pageDistanceMap.put(usedPage, distance);
                            found = true;

                            break;
                        }

                        distance++;
                    }

                    // Swap out pages that will never be used again
                    if (!found)
                        pageDistanceMap.put(usedPage, Integer.MAX_VALUE);
                }

                // Determine the page to swap out
                int maxPage = -1;
                int maxDistance = Integer.MIN_VALUE;
                for (var it : pageDistanceMap.entrySet())
                {
                    if (it.getValue() > maxDistance)
                    {
                        maxDistance = it.getValue();
                        maxPage = it.getKey();
                    }
                }

                // Swap the pages
                frames.replace(maxPage, page);
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

            System.out.printf("Page faults: %d.\n", optimal(new Memory(numFrames), toArray(referenceString)));
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
