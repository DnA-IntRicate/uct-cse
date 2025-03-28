def main():

   print ("Enter an array:")
   grid = []
   for row in range (9):
      grid.append ([])
      line = input ("")
      for col in range (9):
         grid[-1].append (int(line[col:col+1]))

   coordstr = input ("Enter coordinates:\n")
   x, y = list (map (int, coordstr.split (" ")))
   while x>-1 and y>-1:
      print ("Value =", grid[x][y])
      coordstr = input ("Enter coordinates:\n")
      x, y = list (map (int, coordstr.split (" ")))

   print("DONE")

if __name__ == '__main__':
    main()
