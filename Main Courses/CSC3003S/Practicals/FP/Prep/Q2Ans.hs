-- Question 2
-- Adam Foflonker (FFLADA001)
-- 19 Oct 2026
module Q2Ans where

-- Rat definition
data Rat = Rat { ratName :: String } deriving Show

-- Dog definition
data Dog = Dog { dhp :: Int, ddmg :: Int, rats :: [Rat] } deriving Show

-- A Monster
data Monster = Monster { mhp :: Int, mdmg :: Int } deriving Show

-- Rooms
data RoomContents = Fight Monster | Cage Rat | Heal Int | Empty | Escape deriving Show
data Room = Room RoomContents (Maybe Room) (Maybe Room) deriving Show

-- What the result of a dog entering a room could be.
-- Victory holds the final state of Dog so that we can see how many rats the dog
-- recovered.
data VisitResult = Victory Dog | Death | Continue Dog deriving Show

-- HpPoints = 1; RatPoints = 2
score Dog { dhp = dhp, rats = rats } = dhp + ((length rats) * 2)

-- Get the number of rats a Dog has
ratCount :: Dog -> Int
ratCount dog = length $ rats dog

-- Check if the two dogs are equal
instance Eq Dog where
    a == b = score a == score b

-- Rank scores
instance Ord Dog where
    a <= b = score a <= score b

-- VisitResult Eq for use in Ord
instance Eq VisitResult where
    (Victory a)  == (Victory b)  = a == b
    Death        == Death        = True
    (Continue a) == (Continue b) = a == b
    _ == _                       = False

-- Once we have that, we can begin to find out the overall best path through the dungeon.
-- We define Ord here such that x <= y, means that x is a worse result than y for our dog.
instance Ord VisitResult where
    a <= b
      | a == b = True

      -- If both paths continue, the best one is when the dog has the most health.
      -- The best solution is the one that picks up the most rats.
      | (Continue dog) <- a, (Continue dog') <- b = dog <= dog'

      | Death <- a = True  -- matches Death <= any
      | Death <- b = False -- matches any <= Death
      | Victory _ <- b = True  -- matches any <= Victory
      | Victory _ <- a = False -- matches Victory <= any

-- Find the result of our dog fighting a monster (recursive)
fight :: Dog -> Monster -> VisitResult
fight dog mon
  | dhp dog <= 0 = Death
  | mhp mon <= 0 = Continue dog
  | otherwise    = fight dog' mon'
    where
  dog' = (dog { dhp = (dhp dog) - (mdmg mon) })
  mon' = (mon { mhp = (mhp mon) - (ddmg dog) })

-- Find the result of our dog visiting a room.
-- If a dog enters a Cage, it picks up the rat.
visitRoom :: Dog -> RoomContents -> VisitResult
visitRoom dog room = go room
    where
  go (Fight monster) = fight dog monster
  go (Cage rat)      = Continue dog { rats = (rats dog) ++ [rat] }
  go (Heal hp)       = Continue dog { dhp = (dhp dog) + hp }
  go Escape          = Victory dog
  go Empty           = Continue dog
