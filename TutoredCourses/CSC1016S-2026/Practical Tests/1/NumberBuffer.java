// Adam Foflonker
// CSC1016S-2026 Practical Test 1P sample solution
// 03 Sept 2026

public class NumberBuffer
{
    // Create a NumberBuffer that can handle string data comprising integers separated by
    // the character sep i.e. store sep and set data to be an empty string.
    NumberBuffer(char sep)
    {
        separator = sep;
        data = "";
    }

    // Returns true if buffer, i.e. data, is empty, false otherwise.
    public boolean isEmpty()
    {
        return data.isEmpty();
    }

    // Remove the next integer from data (and the following separator if any) and return it.
    public int nextNumber()
    {
        int idx = data.indexOf(separator);
        if (idx < 0)
        {
            int res = Integer.parseInt(data);
            data = "";

            return res;
        }

        int res = Integer.parseInt(data.substring(0, idx));
        data = data.substring(idx + 1);

        return res;
    }

    // Append string to data, ensuring a separator is inserted if data not empty and does not end
    // with one nor string start with one.
    public void addNumbers(String string)
    {
        if (!data.isEmpty()
            && data.charAt(data.length() - 1) != separator
            && (string.isEmpty() || string.charAt(0) != separator)
        )
            data += separator;

        data += string;
    }

    // The string data stored in the NumberBuffer.
    private String data;

    // The character that separates numbers within the string data.
    private char separator;
}
