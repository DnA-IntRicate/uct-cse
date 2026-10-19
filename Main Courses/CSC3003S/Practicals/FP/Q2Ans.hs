-- Functional programming practical test
-- Question 2
-- Adam Foflonker (FFLADA001)
-- 19 Oct 2026
module Q2Ans where

import Data.Maybe (catMaybes)

-- We have no food in Africa :(
data Food = Food Int deriving (Show, Eq)

-- Helper to destructure Food into an int
foodVal :: Food -> Int
foodVal (Food f) = f 

-- Starving dog
data Dog = Dog { foodLevel :: Food } deriving Show

-- A room has contents, and might branch into two more rooms.
-- And some rooms have Food!
data RoomContents = Meal Food | Empty | Escape deriving Show
data Room = Room RoomContents (Maybe Room) (Maybe Room) deriving Show

-- Directly copied from baseGame
data VisitResult = Victory | Death | Continue Dog deriving Show

-- We need to be able to compare the results of dogs entering rooms.
-- The dog with the highest food level wins
instance Ord VisitResult where
    a <= b
      | a == b = True -- matches a <= b IF a == b.

      -- If both paths continue, the best one is when the dog the highest food level
      | (Continue dog) <- a, (Continue dog') <- b = foodVal (foodLevel dog) <= foodVal (foodLevel dog')

      | Death <- a = True  -- matches Death <= any
      | Death <- b = False -- matches any <= Death
      | Victory <- b = True  -- matches any <= Victory
      | Victory <- a = False -- matches Victory <= any

-- To implement Ord we also need to implement Eq.
instance Eq VisitResult where
    Victory      == Victory      = True
    Death        == Death        = True
    (Continue a) == (Continue b) = foodLevel a == foodLevel b
    _ == _                       = False

-- Find the result of our dog visiting a room.
-- The dog dies when the foodVal hits 0.
visitRoom :: Dog -> RoomContents -> VisitResult
visitRoom dog room = go room
    where 
  go (Meal food) = Continue dog { foodLevel = Food ((foodVal (foodLevel dog)) + foodVal food) }
  go Escape      = Victory
  go Empty
    | foodVal (foodLevel dog) - 1 <= 0 = Death
    | otherwise = Continue dog { foodLevel = Food (foodVal (foodLevel dog) - 1) }

-- Directly copied from baseGame
crawl :: Dog -> Room -> VisitResult
crawl dog (Room this left right) = soln
    where 
  soln = case (visitRoom dog this) of
              Continue dog' -> fork dog' left right
              Victory       -> Victory
              Death         -> Death

-- Directly copied from baseGame
fork :: Dog -> Maybe Room -> Maybe Room -> VisitResult
fork dog leftRoom rightRoom = bestPath
    where
  bestPath   = maximum validPaths
  validPaths = catMaybes [leftFirst, rightFirst, leftOnly, rightOnly, Just $ Continue dog]

  leftFirst  = fmap (uncurry $ crawlBoth dog) (both leftRoom rightRoom)
  rightFirst = fmap (uncurry $ crawlBoth dog) (both rightRoom leftRoom)
  leftOnly   = fmap (crawl dog) leftRoom
  rightOnly  = fmap (crawl dog) rightRoom

-- Directly copied from baseGame
crawlBoth :: Dog -> Room -> Room -> VisitResult
crawlBoth dog first second = sequenced
    where
  sequenced = case (crawl dog first) of
                Continue dog' -> crawl dog' second
                Victory       -> Victory
                Death         -> Death

-- Directly copied from baseGame
both :: Maybe a -> Maybe b -> Maybe (a, b)
both (Just a) (Just b) = Just (a, b)
both _        _        = Nothing
