-- Double all even numbers in a list, using lambdas!
doubleAll :: [Int] -> [Int]
doubleAll [] = []
doubleAll nums = map (\x -> x * 2) (filter (\x -> x `mod` 2 == 0) nums)

main :: IO ()
main = do
  let nums = 1 : 2 : 3 : 4 : 5 : 6 : 7 : 8 : 9 : 10 : []
  print (doubleAll nums)
