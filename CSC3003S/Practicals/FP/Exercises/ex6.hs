-- Recursive implementation of foldr
foldr'' :: (a -> b -> b) -> b -> [a] -> b
foldr'' f i []     = i
foldr'' f i (x:xs) = f x (foldr'' f i xs)

-- Merge sort
mergeSort :: Ord a => [a] -> [a]
mergeSort []  = []
mergeSort [x] = [x]
mergeSort xs =
  let (l, r) = splitAt (length xs `div` 2) xs
  in merge (mergeSort l) (mergeSort r)

merge :: Ord a => [a] -> [a] -> [a]
merge [] ys = ys
merge xs [] = xs
merge (x:xs) (y:ys)
  | x <= y    = x : merge xs (y:ys)
  | otherwise = y : merge (x:xs) ys

main :: IO ()
main = do
  let numbers = [99, 8, 2, 54, 33, 0, 8, 4, 24, 35687, 64545, 922, 33, 0]
  print $ foldr (+) 0 numbers
  print $ foldr'' (+) 0 numbers
  print $ mergeSort numbers
