# Adam Foflonker
# FFLADA001
# 12/04/24
# Grid utils

from copy import deepcopy

def create_grid(grid: list[list[int]]):
    """create a 4x4 array of zeroes within grid"""

    for _ in range(4):
        grid.append([0] * 4)

def print_grid(grid: list[list[int]]):
    """print out a 4x4 grid in 5-width columns within a box"""

    print("+--------------------+")

    for i in range(4):
        print('|', end='')

        for j in range(4):
            numStr = "" if grid[i][j] == 0 else str(grid[i][j])
            print(numStr + (' ' * (5 - len(numStr))), end='')

        print('|')

    print("+--------------------+")

def check_lost(grid: list[list[int]]) -> bool:
    """return True if there are no 0 values and there are no adjacent values that are equal; otherwise False"""

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 0:
                return False

            if ((i < len(grid) - 1) and (grid[i][j] == grid[i + 1][j])) or ((j < len(grid[i]) - 1) and (grid[i][j] == grid[i][j + 1])):
                return False

    return True

def check_won(grid: list[list[int]]) -> bool:
    """return True if a value>=32 is found in the grid; otherwise False"""

    for row in grid:
        for num in row:
            if num >= 32:
                return True

    return False

def copy_grid(grid: list[list[int]]) -> list[list[int]]:
    """return a copy of the given grid"""

    return deepcopy(grid)   # We don't want to make a shallow copy here.

def grid_equal(grid1: list[list[int]], grid2: list[list[int]]) -> bool:
    """check if 2 grids are equal - return boolean value"""

    return grid1 == grid2
