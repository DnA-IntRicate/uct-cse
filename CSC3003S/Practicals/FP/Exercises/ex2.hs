data Person = Person
  {
    age :: Int,
    name :: String
  } deriving(Show)

isAdult :: Person -> Bool
isAdult p = (age p) >= 18

-- Recursive function to filter adults (without using built-in filter)
filterAdults :: [Person] -> [Person]
filterAdults [] = []
filterAdults (p:ps)
  | isAdult p = p : filterAdults ps
  | otherwise = filterAdults ps

main :: IO ()
main = do
  let people =
        [ Person 21 "Adam"
        , Person 17 "Eve"
        , Person 18 "Abdul"
        , Person 30 "Charlie"
        , Person 12 "Johnny"
        ]

  -- Filters out Eve & Johnny
  print (filter isAdult people)
  print (filterAdults people)
