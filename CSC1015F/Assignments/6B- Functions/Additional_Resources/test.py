# Unary function execution stub
from sys import argv
module = __import__(argv[1])
function = getattr(module, argv[2])
parameter = input()
print(argv[1]+'.'+argv[2]+'(\''+parameter+'\') =',function(parameter))
