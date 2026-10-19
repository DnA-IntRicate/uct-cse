-- Some tough dungeons
dungeons = [
             Room (Empty) (lr easyMon (lr (Cage jerry) (lr easyMon (only Escape) Nothing) Nothing) Nothing) (only $ Heal 5) `returns` Victory startDog { dhp = 10 - 6 + 5 - 6, rats = [jerry] }
           , Room (Empty) (lr easyMon (lr (Cage jerry) (lr easyMon (only Escape) (only (Cage mickey))) Nothing) Nothing) (only $ Heal 5) `returns` Victory Dog { dhp = 10 - 6 + 5 - 6, ddmg = 1, rats = [jerry, mickey] }
           , Room (Empty) (lr easyMon (lr (Cage jerry) (lr easyMon (only Escape) (lr easyMon (only $ Cage mickey) Nothing)) Nothing) Nothing) (only $ Heal 10) `returns` Victory Dog { dhp = 10 - 6 + 10 - 6, ddmg = 1, rats = [jerry] }
           , Room (Empty) (lr easyMon (lr (Cage jerry) (lr easyMon (only Escape) (lr veryEasyMon (only $ Cage mickey) Nothing)) Nothing) Nothing) (only $ Heal 10) `returns` Victory Dog { dhp = 10 - 6 + 10 - 6 - 1, ddmg = 1, rats = [jerry, mickey] }
           ]

-- Helper functions to define our rooms a little quicker
only contents = Just $ Room contents Nothing Nothing
lr this l r = Just $ Room this l r

-- returnsWithDog = try any dog on the given dungeon, expecting it to return the given result
a `returnsWithDog` (d, b) = (d, a, b)

startDog = Dog { dhp = 10, ddmg = 4, rats = [] }
weakDog = Dog { dhp = 1, ddmg = 1, rats = [] }

-- returns = try startdog on the given dungeon, expecting it to return the given result
a `returns` b = a `returnsWithDog` (startDog, b)

easyMon  = Fight $ Monster 5 3
deathMon = Fight $ Monster 100 1
veryEasyMon = Fight $ Monster 4 1

jerry = Rat "Jerry"
mickey = Rat "Mickey"
