# A program to generate a personalised spam message based on the user's full name, country and a sum of money.
# Author: Adam Foflonker (FFLADA001)
# Date (dd/mm/yyyy): 22/02/2024

firstName = input("Enter first name:\n")
lastName = input("Enter last name:\n")
money = input("Enter sum of money in USD:\n")
country = input("Enter country name:\n")

spamMessage = f'''
Dearest {firstName}
It is with a heavy heart that I inform you of the death of my father,
General Fayk {lastName}, your long lost relative from Mapsfostol.
My father left the sum of {money}USD for us, your distant cousins.
Unfortunately, we cannot access the money as it is in a bank in {country}.
I desperately need your assistance to access this money.
I will even pay you generously, 30% of the amount - {eval(money) * (30 / 100)}USD,
for your help.  Please get in touch with me at this email address asap.
Yours sincerely
Frank {lastName}
'''

print(spamMessage)
