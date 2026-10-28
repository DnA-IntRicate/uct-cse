-- Model solution (see the slides)
-- Last update: 16 Oct, 12:20.
--
-- Corrections since the lecture:
-- - Changed dhp dog == 0 and mhp mon == 0 to <= 0 in both
-- - Changed implementation of Ord to be more explicit for every possibility

import Data.Maybe (catMaybes)
import Data.Tree ( Tree(..), drawTree ) -- This is needed for the last section
import Data.List (intercalate)        -- This is needed for the last section

-- A room has contents, and might branch into two more rooms.
-- The wizard promised we won't ever have a cycle (rooms can't connect to previous rooms).
-- Therefore, Room is a _tree_ datastructure
data Room = Room RoomContents (Maybe Room) (Maybe Room) deriving Show
data RoomContents = Fight Monster | Heal Int | Empty | Escape deriving Show

-- Our dog :)
data Dog = Dog { dhp :: Int, ddmg :: Int } deriving Show

-- A monster! :o
data Monster = Monster { mhp :: Int, mdmg :: Int } deriving Show

-- What the result of a dog entering a room could be
-- They can either:
-- 1. Victory: escape
-- 2. Death: die
-- 3. Continue: be able to continue in the dungeon; alive but not free yet.
data VisitResult = Victory | Death | Continue Dog deriving Show

-- We need to be able to compare the results of dogs entering rooms
-- That way, we can say whether going left is a _better choice_ than right or not
-- Once we have that, we can begin to find out the overall best path through the dungeon.
-- We define Ord here such that x <= y means that x is a _worse result_ than y for our dog
instance Ord VisitResult where
    a <= b
      -- == obviously implies <=, since <= is defined as < or ==
      | a == b = True      -- matches a <= b IF a == b.

      -- If both paths continue, the best one is when the dog has the most health
      | (Continue dog) <- a, (Continue dog') <- b = (dhp dog) <= (dhp dog')

      -- Now we've ruled out == from <=, we just need to implement < for the rest

      -- Death is worse than anything else, and anything is better than Death
      | Death <- a = True  -- matches Death <= any
      | Death <- b = False -- matches any <= Death

      -- Victory is better than anything else, and anything is worse than Victory
      | Victory <- b = True  -- matches any <= Victory
      | Victory <- a = False -- matches Victory <= any

      -- DIFFERENCE FROM THE LECTURE: I got rid of the otherwise case to make it
      -- easier to see what is happening here.


-- To implement Ord we also need to implement Eq.
-- Our ddmg shouldn't ever change, so we only compare HP here
-- And we won't compare dogs from different dungeons, so we don't 
-- need to worry about dogs with different dmg values being compared
instance Eq VisitResult where
    Victory      == Victory      = True
    Death        == Death        = True
    (Continue a) == (Continue b) = (dhp a) == (dhp b)
    _ == _                       = False

-- Find the result of our dog fighting a monster
fight :: Dog -> Monster -> VisitResult
fight dog mon
  | dhp dog <= 0 = Death
  | mhp mon <= 0 = Continue dog
  | otherwise    = fight dog' mon'
    where
  dog' = (dog { dhp = (dhp dog) - (mdmg mon) })
  mon' = (mon { mhp = (mhp mon) - (ddmg dog) })

-- Find the result of our dog visiting a room.
-- This _only_ processes what is inside THAT room. Not the room's children (left + right room)
-- This is the CONQUER part of our divide and conquer approach.
visitRoom :: Dog -> RoomContents -> VisitResult
visitRoom dog room = go room
    where 
  go (Fight monster) = fight dog monster
  go (Heal hp)       = Continue dog { dhp = (dhp dog) + hp }
  go Escape          = Victory
  go Empty           = Continue dog

-- Find the result of our dog visiting a room AND its children rooms.
-- This essentially solves the subtree rooted at the given room.
crawl :: Dog -> Room -> VisitResult
crawl dog (Room this left right) = soln
    where 
  soln = case (visitRoom dog this) of
              Continue dog' -> fork dog' left right
              Victory       -> Victory
              Death         -> Death

-- Find the result of our dog visiting ONLY the room's children. It is the counterpart to visitRoom.
-- Notice how crawl = fork + visitRoom.
-- This is our DIVIDE part of our divide and conquer approach.
fork :: Dog -> Maybe Room -> Maybe Room -> VisitResult
fork dog leftRoom rightRoom = bestPath
    where
  -- The best path for the dog is the _highest scoring_ valid path.
  -- This uses our instance Ord VisitResult where
  bestPath   = maximum validPaths

  -- Our possible valid paths.
  -- An _invalid_ path would be Nothing here, and represents e.g. going to the left room,
  -- if there _is_ no left room. catMaybes filters these out into paths that CAN be done.
  validPaths = catMaybes [leftFirst,     rightFirst,      leftOnly,     rightOnly,   Just $ Continue dog]
  --                     ^^^^^^^^^^^^^^^^^^^^^^           ^^^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^
  --                     visit both child rooms             visit just one child     don't visit children
  --                   (left -> right,  right -> left)    (left)          (right)

  -- Define the valid paths
  leftFirst  = fmap (uncurry $ crawlBoth dog) (both leftRoom rightRoom)
  rightFirst = fmap (uncurry $ crawlBoth dog) (both rightRoom leftRoom)
  leftOnly   = fmap (crawl dog) leftRoom
  rightOnly  = fmap (crawl dog) rightRoom


-- Find the result of our dog visiting the first room and THEN the second room, in sequence.
crawlBoth :: Dog -> Room -> Room -> VisitResult
crawlBoth dog first second = sequenced
    where
  sequenced = case (crawl dog first) of
                Continue dog' -> crawl dog' second
                Victory       -> Victory
                Death         -> Death

-- Convert two maybes into one. We get a Just out when both maybes are Just.
both :: Maybe a -> Maybe b -> Maybe (a, b)
both (Just a) (Just b) = Just (a, b)
both _        _        = Nothing



-- Defines sample dungeons. NOT USED BY THE AUTOMARKER, ONLY BY YOU TO TEST
-- YOUR SOLUTION.

-- Helper functions to define our rooms a little quicker
only contents = Just $ Room contents Nothing Nothing
lr this l r = Just $ Room this l r

-- returnsWithDog = try any dog on the given dungeon, expecting it to return the given result
a `returnsWithDog` (d, b) = (d, a, b)

startDog = Dog { dhp = 10, ddmg = 4 }
weakDog = Dog { dhp = 1, ddmg = 1 }

-- returns = try startdog on the given dungeon, expecting it to return the given result
a `returns` b = a `returnsWithDog` (startDog, b)

easyMon  = Fight $ Monster 5 3
deathMon = Fight $ Monster 100 1

dungeons :: [(Dog, Room, VisitResult)]
dungeons = [
             Room Escape (only deathMon) Nothing `returns` Victory
           , Room (deathMon) (only Escape) (Nothing) `returns` Death
           , Room (Empty) (only Escape) (Nothing) `returns` Victory
           , Room (Empty) (Nothing) (only Escape) `returns` Victory
           , Room (Empty) (only Empty) (only Escape) `returns` Victory
           , Room (Empty) (only deathMon) (only Escape) `returns` Victory
           , Room (Empty) (only easyMon) Nothing `returns` Continue startDog
           , Room (easyMon) (Nothing) (Nothing) `returns` Continue Dog { dhp = 4, ddmg = 4 }
           , Room (Empty) (only easyMon) (only Empty) `returns` Continue startDog
           , Room (Empty) (lr easyMon (only easyMon) (only Escape)) (only deathMon) `returns` Victory
           , Room (Empty) (lr easyMon (lr (Heal 5) (lr easyMon (only Escape) Nothing) Nothing) Nothing) (only deathMon) `returns` Victory
           , Room (Empty) (lr easyMon (lr Empty (lr easyMon (only Escape) Nothing) Nothing) Nothing) (only $ Heal 5) `returns` Victory
           , Room (Empty) (lr easyMon (lr Empty (lr easyMon (only Escape) Nothing) Nothing) Nothing) (only $ Heal 5) `returns` Victory
           , Room (Empty) (lr easyMon (lr Empty (lr easyMon (only Escape) Nothing) Nothing) Nothing) (only $ Heal 5) `returnsWithDog` (weakDog, Continue Dog { dhp = 6, ddmg = 1 })
           , Room (Empty) (lr easyMon (lr Empty (lr easyMon (only Escape) Nothing) Nothing) Nothing) (lr easyMon (only $ Heal 100) Nothing) `returns` Victory
           ]

-- =====================================================================
-- EVERYTHING BELOW HERE IS JUST TO TEST OUR ALGORITHM ON SAMPLE INPUTS
-- You won't need to define this any differently yourself. You can just
-- copy paste them to test, in the exam. So, you don't really need to
-- understand how this works.
-- 
-- The automarker will NEVER invoke your main function!
-- It will use your types (Room, Dog, Monster, RoomType, etc...) and your
-- crawl function.
-- =====================================================================



-- See how _easy_ and _simple_ tree traversal and mapping is with recursion in Haskell? ;)
dungeonToTree :: Room -> Tree String
dungeonToTree (Room this left right) = Node { rootLabel = show this, subForest = map dungeonToTree $ catMaybes [left, right] }

-- Function composition FTW!
drawDungeon :: Room -> String
drawDungeon =  drawTree . dungeonToTree

indent :: String -> String
indent = unlines . map ("    " ++) . lines

printAndCrawl :: (Int, (Dog, Room, VisitResult)) -> IO Bool
printAndCrawl (n, (dog, dungeon, expected)) = do
    putStrLn $ "==== Dungeon crawl! Trial: " ++ show n ++ " ===="
    putStrLn $ "Our dog: \n"
    putStrLn ("    " ++ (show dog))
    putStrLn "\nOur dungeon:\n"
    putStrLn $ indent $ drawDungeon dungeon

    let result = crawl dog dungeon
    let success = result == expected

    putStrLn $ "Trial " ++ (if success then "successful!" else "failed!")
    putStrLn $ "The result: " ++ (show result)
    putStrLn $ "Expected result: " ++ (show expected)
    putStrLn "\n\n"

    pure success

main :: IO ()
main = do 
  results <- mapM printAndCrawl $ zip [0..] dungeons
  putStrLn "======================== SUMMARY ========================"
  let failed = filter (== False) results
  let success = filter (== True) results

  putStrLn $ "Successful: " ++ (show $ length success) ++ ". Failed: " ++ (show $ length failed)

  if (length failed) > 0 then do
    let failedPretty = intercalate ", " $ map (show . fst) $ filter ((== False) . snd) $ zip [0..] results
    putStrLn $ "\nFailed on trials: " ++ failedPretty
  else
    pure ()
