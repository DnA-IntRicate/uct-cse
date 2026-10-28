// Adam Foflonker
// FFLADA001
// 7 August 2024
// Class to represent a car park ticket


public class Ticket
{
    // Create a new Ticket that has the given issue time and unique ID
    public Ticket(Time currentTime, String ID)
    {
        id = ID;
        issueTime = currentTime;
    }

    // Obtain this Ticket's ID
    public String ID()
    {
        return id;
    }

    // Obtain this ticket's age i.e. the issue time subtracted from the given time.
    public Duration age(Time currentTime)
    {
        return currentTime.subtract(issueTime);
    }

    // Obtain a String representation of this Ticket object in the form: 'Ticket[id="ddddd", time="hh:mm:ss"]'
    public String toString()
    {
        return String.format("Ticket[id=%s, time=%s]", id, issueTime.toString());
    }

    private String id;
    private Time issueTime;
}
