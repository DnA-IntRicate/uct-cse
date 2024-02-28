# Program to count the number of odd numbers entered by the user
# Stephan Jamieson
# 15th February 2024

count = 0
response = input("number:\n")

while response:
 value = int(response)

 if value % 2 == 1:
  print('odd')
  count = count + 1
  response = input("number:\n")
 else:
  print('even')
  response = input("number:\n")

print('num odd:', count, end='.\n')