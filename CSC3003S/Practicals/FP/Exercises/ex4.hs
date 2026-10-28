-- Implementing my own versions of 'sum', 'map' & 'filter'
-- with the constraint that 'foldl' must be used.

sum' :: [Int] -> Int
sum' nums = foldl (+) 0 nums

map' :: (a -> b) -> [a] -> [b]
map' f [] = []
map' f l = reverse $ foldl (\acc x -> f x : acc) [] l

filter' :: (a -> Bool) -> [a] -> [a]
filter' f [] = []
filter' f l = reverse $ foldl (\acc x -> if (f x) then x : acc else acc) [] l

main :: IO ()
main = do
  let numbers = [5, 10, 2, 3]

  print $ sum' numbers
  print $ map' (* 2) numbers
  print $ filter' (\x -> mod x 2 == 0) numbers
