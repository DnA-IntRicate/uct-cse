The wizard has stolen the class dog… but he’s also stolen one of your pet rats! You should try fetch it also if possible. 

If your dog would hurt at all in order to fetch the rat, then leave it behind (it’ll probably find a way out on its own eventually, since it can burrow...)

This means means that if you have two paths that end in Victory, where one gets a rat and one doesn't, the path with the rat should have the same (or more) HP than the one which _doesn't_ get the rat.

So, if the dog loses 4 HP, gains the rat, and then gains back 4 HP, this is _better_ than skipping the rat. But, if it loses 4 HP, gains the rat, and gains back only 3 HP, you should skip the rat.


# Question 1

## Question 1.1
Implement a type for Rat. Give it a member ratName of type String. You should be able to get the data from Rat using the ratName :: Rat -> String function.

You should be able to construct a rat with the following constructors (functions)
```haskell
Rat :: String -> Rat
```

and get the name of a rat with the folowing function
```haskell
ratName :: Rat -> String
```

You should also derive `Show` for your `Rat` (add `deriving Show` to the end of the definition).

## Question 1.2
Add a member `rat` to the Dog type. Make sure it is of type Maybe Rat.

You should now be able to construct the dog with `Dog { dhp = 1, ddmg = 2, rat = Just myRat }`, where `myRat` is a `Rat`.

## Question 1.3
Add a variant to the `RoomContents` type for a room with the rat in it. Call it `Cage`. It should have a value of type `Rat`.

## Question 1.4
Modify the Eq implementation for Dog to check the two Dogs given both have rats. If they don’t, then the dogs won’t be equal.

## Question 1.5
Modify the Ord implementation for VisitResult such that when comparing `Continue dog`s, dogs without a rat are less than dogs with a rat, IF their healths are equal. So `Continue (Dog 10 2 Nothing) <= Continue (Dog 10 2 (Just Rat “Jeremy”))`, BUT `Continue (Dog 4 2 (Just Rat “Jeremy”)) <= Continue (Dog 10 2 Nothing)`

## Question 1.6
Modify the `visitRoom` function so that, if a dog enters a `Cage` room, it picks up the rat.

# Question 2

OH NO! ALL YOUR PET RATS HAVE BEEN TAKEN! (not just the one)

Implement the full solution for dungeons that can have multiple rats in them. Still only one per room, though.

You’ll need to:

i) modify `Dog` to hold multiple rats (call the member `rats`).
ii) Implement a function to get how many rats a dog has. It should be called `ratCount`, take a `Dog`, and return an `Int`.
iii) modify `VisitResult`'s `Victory` variant to hold the final state of the `Dog`, so that we can see how many rats the `Dog` fetched.
iv) modify `visitRoom` to pick up a rat when in a room with a rat.
v) modify the `Eq` and `Ord` implementations for Dog so that the best solution is one that picks up the most rats. **This time, one rat is worth 2 health points of the dog. So, a solution involving a dog with 10 HP and 5 rats is better than a dog with 19 HP and no rats. Still avoid death, though.**
