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
 * Java implementation of CSC1015F-2024 Assignment 5, Question 3.
 *
 * @author Adam Foflonker
 * @version 08/20/24
 */
public class Breakup
{
    /**
     * Sample Input and Output:
     *
     * <pre>
     * Input:
     * Case 1: "Jerusalema ikhaya LAMI"
     * Case 2: "The Quick Brown Fox Jumped Over The Lazy Dog"
     *
     * Output:
     * Case 1: "jerusalema, ikhaya, lami"
     * Case 2: "the, quick, brown, fox, jumped, over, the, lazy, dog."
     * </pre>
     */
    public static void main(String[] args)
    {
        System.out.println("Enter a sentence:");

        String inSentence;
        try (Scanner scanner = new Scanner(System.in)) { inSentence = scanner.nextLine(); }

        try (Scanner senScanner = new Scanner(inSentence))
        {
            System.out.print("The word list: ");

            senScanner.useDelimiter("\\s+");
            while (senScanner.hasNext())
            {
                String word = senScanner.next().toLowerCase();
                System.out.print(word + (senScanner.hasNext() ? ", " : "."));
            }
        }
    }
}
