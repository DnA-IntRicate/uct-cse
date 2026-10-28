isPalindrome :: String -> Bool
isPalindrome s = s == (reverse s)

palindromes :: [String] -> [String]
palindromes l = filter isPalindrome l

main :: IO ()
main = do
  -- Returns ["aba", "racecar"]
  print (palindromes ["aba", "abb", "hello", "racecar"])
