/**
 * Sample usage for {@link Shift} and {@link Employee}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 12/09/24
 */
public class EmployeeShiftTest
{
    private EmployeeShiftTest() { };

    public static void main(String[] args)
    {
        Employee em = new Employee("Sivuyile Ngesi", "01010125");

        em.signIn(new Date("21/1/2019"), new Time("6:00"));
        em.signOut(new Date("21/1/2019"), new Time("14:00"));

        em.signIn(new Date("22/1/2019"), new Time("16:00"));
        em.signOut(new Date("23/1/2019"), new Time("1:00"));

        em.signIn(new Date("23/1/2019"), new Time("18:00"));
        em.signOut(new Date("24/1/2019"), new Time("2:00"));

        for (final Shift s : em.get(new Week("4/2019")))
            System.out.println(s.toString());

        System.out.println(Duration.format(em.hours(new Week("4/2019")), "minute"));
        System.out.println(em.worked(new Date("22/1/2019")));
    }
}
