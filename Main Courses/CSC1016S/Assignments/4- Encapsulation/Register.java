// Adam Foflonker
// FFLADA001
// 7 August 2024
// Register class to manage all active car park tickets


public class Register
{
    // Create a new Register object.
    public Register()
    {
        tickets = new Ticket[100];  // The maximum length of the tickets array is 100
        numTickets = 0;
    }

    // Store the given ticket in the register
    public void add(Ticket ticket)
    {
        // Programmers should be lazy, and I... am lazy :)
        tickets[numTickets++] = ticket;
    }

    // Determine whether a ticket with the given ID is in the collection
    public boolean contains(String ticketID)
    {
        for (int i = 0; i < numTickets; ++i)
        {
            if (tickets[i].ID().equals(ticketID))
                return true;
        }

        return false;
    }

    // Get the Ticket with the given ID from the collection.
    public Ticket retrieve(String ticketID)
    {
        for (int i = 0; i < numTickets; ++i)
        {
            if (tickets[i].ID().equals(ticketID))
                return tickets[i];
        }

        return null;
    }

    private Ticket[] tickets;
    private int numTickets;
}
