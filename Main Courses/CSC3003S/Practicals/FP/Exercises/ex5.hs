data StreetAddress = Addr
  {
    number :: Int
  , street :: String
  } -- deriving Show

instance Show StreetAddress where
  show addr = "Addr(" ++ (show $ number addr) ++ " " ++ (street addr) ++ ")"

-- Sum with a fold expression
sum' :: Num a => [a] -> a
sum' l = foldl (+) 0 l

-- Sum recursive
sum'' :: Num a => [a] -> a
sum'' []     = 0
sum'' (x:xs) = x + sum'' xs

-- My own implementation of 'Maybe' & 'mapMaybe'.
-- Original implementation is found in 'Data.Maybe'.
mapMaybe' :: (a -> Maybe b) -> [a] -> [b]
mapMaybe' f [] = []
mapMaybe' f (x:xs) =
  case f x of
    Nothing -> mapMaybe' f xs
    Just y -> y : mapMaybe' f xs

-- Test out the mapMaybe' function
keepEven :: Int -> Maybe Int
keepEven x
    | even x    = Just x
    | otherwise = Nothing

main :: IO ()
main = do
  let addr = Addr 117 "Big Road"
  print addr

  let numbers = [5, 10, 2, 3]
  print $ sum' numbers
  print $ sum'' numbers

  -- Outputs [10,2]
  print $ mapMaybe' keepEven numbers
