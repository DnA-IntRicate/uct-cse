// Adam Foflonker
// FFLADA001
// Practical Test 1
// 22 August 2024

public class Mutator
{
    private String map;

    public Mutator(String mapString)
    {
        this.map = mapString;
    }

    public char map(char c)
    {
        for (int i = 0; i < this.map.length(); i += 2)
        {
            if (this.map.charAt(i) == c)
                return this.map.charAt(i + 1);
        }

        return c;
    }

    public String mutate(String target)
    {
        String res = "";
        for (int i = 0; i < target.length(); ++i)
            res += map(target.charAt(i));

        return res;
    }
}
