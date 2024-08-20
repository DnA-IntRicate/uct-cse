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
 * Java implementation of CSC1015F-2024 Assignment 5, Question 4.
 *
 * @author Adam Foflonker
 * @version 08/20/24
 */
public class PigLatin
{
    /**
     * Checks whether the given char is a vowel or not.
     *
     * @param c the char to check.
     * @return {@code true} if {@code c} is a vowel, {@code false} otherwise.
     */
    public static boolean IsVowel(final char c)
    {
        return "aeiou".indexOf(Character.toLowerCase(c)) != -1;
    }

    /**
     * Converts the given string to Pig Latin.
     *
     * @param s the string to convert.
     * @return The string {@code s} in Pig Latin.
     */
    public static String ToPigLatin(final String s)
    {
        if (IsVowel(s.charAt(0)))
            return s + "way";

        String consonantSeq = "";
        for (int i = 0; i < s.length(); ++i)
        {
            if (IsVowel(s.charAt(i)))
                break;

            consonantSeq += s.charAt(i);
        }

        return s.substring(consonantSeq.length()) + 'a' + consonantSeq + "ay";
    }

    /**
     * Sample Input and Output:
     *
     * <pre>
     * Input:
     * Case 1: "The quick black fox jumps over the lazy apple"
     *
     * Output:
     * Case 1: "eathay uickaqay ackablay oxafay umpsajay overway eathay azyalay appleway"
     * </pre>
     */
    public static void main(String[] args)
    {
        System.out.println("Enter a sentence:");

        String inSentence;
        try (Scanner scanner = new Scanner(System.in)) { inSentence = scanner.nextLine(); }

        try (Scanner senScanner = new Scanner(inSentence))
        {
            senScanner.useDelimiter("\\s+");
            while (senScanner.hasNext())
            {
                String word = ToPigLatin(senScanner.next().toLowerCase());
                System.out.print(word + (senScanner.hasNext() ? " " : ""));
            }
        }
    }
}
