import java.util.Scanner;


public class Clock
{
    private static int clock(final Memory frames, final Integer[] pageReferences)
    {
        int pageFaults = 0;
        int[] refBits = new int[frames.size()];
        int clockHand = 0;

        for (int page : pageReferences)
        {
            // Handle page hit
            if (frames.contains(page))
            {
                // Set reference bit = 1
                int index = frames.indexOf(page);
                refBits[index] = 1;

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
                    refBits[frame] = 1;
                    inserted = true;

                    System.out.printf("%d: %s\n", page, frames);
                    break;
                }
            }

            // If no empty frame is found, perform the Clock (Second Chance) page replacement
            if (!inserted)
            {
                while (true)
                {
                    // Evict pages with a reference bit of 0
                    if (refBits[clockHand] == 0)
                    {
                        // Swap the pages and update reference bit
                        frames.put(clockHand, page);
                        refBits[clockHand] = 1;
                        clockHand = (clockHand + 1) % frames.size();

                        System.out.printf("%d: %s\n", page, frames);
                        break;
                    }
                    else // Second chance
                    {
                        refBits[clockHand] = 0;
                        clockHand = (clockHand + 1) % frames.size();
                    }
                }
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

            System.out.printf("Page faults: %d.\n", clock(new Memory(numFrames), toArray(referenceString)));
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
