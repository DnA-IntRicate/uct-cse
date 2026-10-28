/**
 * Represents a mating for use in {@link Population}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 01/03/25
 */
public class Mating
{
    public Mating(Critter critterA, Critter critterB)
    {
        m_CritterA = critterA;
        m_CritterB = critterB;
    }

    /**
     * Let's get BUSY!
     *
     * @return the {@link Critter} offspring of the mating
     */
    public Critter Mate()
    {
        String codeA = m_CritterA.GetGeneticCode();
        String codeB = m_CritterB.GetGeneticCode();

        String resCode = "";
        if (codeA.length() == codeB.length())
        {
            for (int i = 0; i < codeA.length(); ++i)
            {
                resCode += Character.toString(codeA.charAt(i)) + Character.toString(codeB.charAt(i));

                if (resCode.length() == 10)
                    return new Critter(resCode);
            }

            return new Critter(resCode); // All characters of codeA and codeB have been used
        }

        // This could be done differently but the order of codeA and codeB cant be alternated.
        if (codeA.length() > codeB.length())
        {
            for (int i = 0; i < codeB.length(); ++i)
            {
                resCode += Character.toString(codeA.charAt(i)) + Character.toString(codeB.charAt(i));

                if (resCode.length() == 10)
                    return new Critter(resCode);
            }

            resCode += codeA.substring(codeB.length(), codeA.length());
            resCode = (resCode.length() > 10) ? resCode.substring(0, 10) : resCode; // Cap length at 10

            return new Critter(resCode);
        }

        for (int i = 0; i < codeA.length(); ++i)
        {
            resCode += Character.toString(codeA.charAt(i)) + Character.toString(codeB.charAt(i));

            if (resCode.length() == 10)
                return new Critter(resCode);
        }

        resCode += codeB.substring(codeA.length(), codeB.length());
        resCode = (resCode.length() > 10) ? resCode.substring(0, 10) : resCode; // Cap length at 10

        return new Critter(resCode);
    }

    public Critter GetCritterA() { return m_CritterA; }
    public Critter GetCritterB() { return m_CritterB; }

    private Critter m_CritterA;
    private Critter m_CritterB;
}
