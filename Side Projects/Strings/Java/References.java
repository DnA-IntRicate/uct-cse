/**********************************************************************************
* MIT License
*
* Copyright (c) 2024 Adam Foflonker
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all
* copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
***********************************************************************************/

import java.util.Scanner;

/**
 * Java implementation of CSC1015F-2024 Assignment 5, Question 1.
 *
 * @author Adam Foflonker
 * @version 08/20/24
 */
public class References
{
    /**
     * Capitalizes the first letter of each word in {@code s}. Makes everything else lower-case.
     *
     * @param s the string to capitalize.
     * @return The capitalized string.
     */
    public static String Capitalize(final String s)
    {
        String res = "";
        for (final var word : s.toLowerCase().split("\\s+"))
            res += Character.toUpperCase(word.charAt(0)) + word.substring(1) + " ";

        return res.trim();
    }

    /**
     * Capitalizes only the first letter of the first word in {@code s}. Makes everything else lowercase.
     *
     * @param s string to convert to a title.
     * @return The string as a title.
     */
    public static String Title(final String s)
    {
        return Character.toUpperCase(s.charAt(0)) + s.substring(1).toLowerCase();
    }

    /**
     * Sample Input and Output:
     *
     * <pre>
     * Input:
     * Case 1: "suleman, h (2001) Some Random Piece Of Junk, Journal of Junk, ACM, pp1-100, 2000"
     * Case 2: "POULO, lebeko bernard (2013) fine-grained scalability Of digital library services In The cloud, SAICSIT Conference 2014, ACM, pp23-34, 2014"
     *
     * Output:
     * Case 1: "Suleman, H (2001) Some random piece of junk, Journal of Junk, ACM, pp1-100, 2000"
     * Case 2: "Poulo, Lebeko Bernard (2013) Fine-grained scalability of digital library services in the cloud, SAICSIT Conference 2014, ACM, pp23-34, 2014"
     * </pre>
     */
    public static void main(String[] args)
    {
        System.out.println("Enter the reference:");

        // Using a 'try-with-resources' block to automatically free all resources held by the scanner when it falls
        // out of scope.
        String inRef;
        try (Scanner scanner = new Scanner(System.in)) { inRef = scanner.nextLine(); }

        // These can be marked as 'final' since their values NEVER get reassigned after creation.
        // In another words, they should remain 'readonly.'
        final int firstParen = inRef.indexOf('(', 0);
        final int lastParen = inRef.indexOf(')', 0);
        final int titleBeg = lastParen + 2;
        final int titleEnd = inRef.indexOf(',', titleBeg);

        final String names = Capitalize(inRef.substring(0, firstParen).trim());
        final String year = inRef.substring(firstParen, lastParen + 1).trim();
        final String title = Title(inRef.substring(titleBeg, titleEnd).trim());

        System.out.println("Reformatted reference:");
        System.out.printf("%s %s %s%s\n", names, year, title, inRef.substring(titleEnd));
    }
}
