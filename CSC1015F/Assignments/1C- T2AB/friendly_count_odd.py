# Program to count the number of odd numbers entered by the user
# Stephan Jamieson
# 15th February 2024

count = 0
response = input("Enter a number (or just press enter to quit):\n")

while response:
 value = int(response)

 if value % 2 == 1:
  print('That number is odd.')
  count = count + 1
  response = input("Enter a number (or just press enter to quit):\n")
 else:
  print('That number is even.')
  response = input("Enter a number (or just press enter to quit):\n")

print('Okay, the number odd numbers entered is', count, end='.\n')
