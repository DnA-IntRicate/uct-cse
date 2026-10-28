-- Question 1
-- Adam Foflonker (FFLADA001)
-- 19 Oct 2026
module Q1Ans where

-- Q: 1.1
data Rat = Rat { ratName :: String } deriving Show

-- Q: 1.2
data Dog = Dog { dhp :: Int, ddmg :: Int, rat :: Maybe Rat } deriving Show

-- A Monster
data Monster = Monster { mhp :: Int, mdmg :: Int } deriving Show

-- Q: 1.3
-- A room has contents, and might branch into two more rooms.
-- The wizard promised we won't ever have a cycle (rooms can't connect to previous rooms).
-- Therefore, Room is a _tree_ datastructure
data RoomContents = Fight Monster | Cage Rat | Heal Int | Empty | Escape deriving Show
data Room = Room RoomContents (Maybe Room) (Maybe Room) deriving Show

-- What the result of a dog entering a room could be
-- They can either:
-- 1. Victory: escape
-- 2. Death: die
-- 3. Continue: be able to continue in the dungeon; alive but not free yet.
data VisitResult = Victory | Death | Continue Dog deriving Show

-- Helper for checking Maybe values
isJust :: Maybe a -> Bool
isJust Nothing  = False
isJust (Just _) = True
hasRat dog = isJust (rat dog)

-- Q: 1.4
-- Check if the two dogs both have rats. If not, they're unequal.
instance Eq Dog where
    a == b = (dhp a == dhp b) && (hasRat a == hasRat b)

-- To implement Ord we also need to implement Eq.
-- Our ddmg shouldn't ever change, so we only compare HP here
-- And we won't compare dogs from different dungeons, so we don't
-- need to worry about dogs with different dmg values being compared
instance Eq VisitResult where
    Victory      == Victory      = True
    Death        == Death        = True
    (Continue a) == (Continue b) = a == b
    _ == _                       = False

-- We need to be able to compare the results of dogs entering rooms
-- That way, we can say whether going left is a better choice than right or not
-- Once we have that, we can begin to find out the overall best path through the dungeon.
-- We define Ord here such that x <= y, means that x is a worse result than y for our dog.
instance Ord VisitResult where
    a <= b
      | a == b = True      -- matches a <= b IF a == b.

      -- Q: 1.5
      -- If both paths continue, the best one is when the dog has the most health
      -- Dogs without a rat are less than dogs with a rat if their healths are equal
      -- Ord for tuple as used here compares the two first elems. If they are equal, it compares the second elems. So here the HP
      -- takes precedence over the amount of rats
      | (Continue dog) <- a, (Continue dog') <- b = (dhp dog, hasRat dog) <= (dhp dog', hasRat dog')

      -- Now we've ruled out == from <=, we just need to implement < for the rest
      | Death <- a = True  -- matches Death <= any
      | Death <- b = False -- matches any <= Death
      | Victory <- b = True  -- matches any <= Victory
      | Victory <- a = False -- matches Victory <= any

-- Find the result of our dog fighting a monster (recursive)
fight :: Dog -> Monster -> VisitResult
fight dog mon
  | dhp dog <= 0 = Death
  | mhp mon <= 0 = Continue dog
  | otherwise    = fight dog' mon'
    where
  dog' = (dog { dhp = (dhp dog) - (mdmg mon) })
  mon' = (mon { mhp = (mhp mon) - (ddmg dog) })

-- Q: 1.6
-- Find the result of our dog visiting a room.
-- This only processes what is inside THAT room. Not the room's children (left + right room).
-- If a dog enters a Cage, it picks up the rat.
visitRoom :: Dog -> RoomContents -> VisitResult
visitRoom dog room = go room
    where
  go (Fight monster) = fight dog monster
  go (Cage rat)      = Continue dog { rat = Just rat }
  go (Heal hp)       = Continue dog { dhp = (dhp dog) + hp }
  go Escape          = Victory
  go Empty           = Continue dog
