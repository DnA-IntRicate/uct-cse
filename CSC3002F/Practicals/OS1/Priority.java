import java.util.Arrays;
import java.util.Scanner;
//
public class Priority 
{

    private static int priority(final Memory frames, final Integer[] pageReferences, final Integer[] pagePriorities) 
    {
        int pageFaults = 0;

        for (var page : pageReferences)
        {
            // Decrement priority
            pagePriorities[page]--;

            // Page hit
            if (frames.contains(page))
            {
                // Decrement priority
                // pagePriorities[page]--;

                System.out.printf("%d: -\n", page);
                continue;
            }

            pageFaults++;

            // Fill initial pages from empty
            boolean inserted = false;
            for (int frame = 0; frame < frames.size(); ++frame)
            {
                if (frames.isEmpty(frame))
                {
                    // Decrement priority
                    // pagePriorities[page]--;

                    frames.put(frame, page);
                    System.out.printf("%d: %s\n", page, frames);

                    inserted = true;
                    break;
                }
            }

            if (inserted)
                continue;

            int lowestPriority = Integer.MAX_VALUE;
            int pageToEvict = -1;
            int frameToEvict = -1;

            for (int frame = 0; frame < frames.size(); ++frame)
            {
                int currentPage = frames.get(frame);
                if (pagePriorities[currentPage] < lowestPriority)
                {
                    lowestPriority = pagePriorities[currentPage];
                    pageToEvict = currentPage;
                    frameToEvict = frame;
                }
                else if (pagePriorities[currentPage] == lowestPriority)   // Tiebreaker
                {
                    pageToEvict = (pageToEvict > currentPage) ? currentPage : pageToEvict;
                    frameToEvict = frames.indexOf(pageToEvict);
                }
            }

            // Page replacement
            frames.put(frameToEvict, page);
            System.out.printf("%d: %s\n", page, frames);
        }

        return pageFaults;
    }


    public static void main(final String[] args) {
        final Scanner stdIn = new Scanner(System.in);

        System.out.println("Enter the physical memory size (number of frames):");
        final int numFrames = stdIn.nextInt();
        stdIn.nextLine();

        System.out.println("Enter the string of page references:");
        final String referenceString = stdIn.nextLine();

        System.out.println("Enter the page priorities:");
        final String priorityString = stdIn.nextLine();

        System.out.printf("Page faults: %d.\n", priority(new Memory(numFrames), toArray(referenceString), parsePriorities(priorityString)));
    }

    private static Integer[] toArray(final String referenceString) {
        final Integer[] result = new Integer[referenceString.length()];

        for(int i=0; i < referenceString.length(); i++) {
            result[i] = Character.digit(referenceString.charAt(i), 10);
        }
        return result;
    }

    private static Integer[] parsePriorities(final String priorityString) {
        final Integer[] priorities = new Integer[10];

        final Scanner scanner = new Scanner(priorityString);
        while (scanner.hasNext()) {
            final Scanner term = new Scanner(scanner.next());
            term.useDelimiter(":");
            final int page = term.nextInt();
            final Integer priority = term.nextInt();
            priorities[page] = priority;
        }
        return priorities;
    }
}
