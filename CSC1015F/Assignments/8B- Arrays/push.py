# Adam Foflonker
# FFLADA001
# 16/04/24
# Grid value merging routines for 2048.py

# Create a copy of the row-major grid as column-major
def TransposeGrid(grid: list[list[int]]) -> list[list[int]]:
    newGrid = [[0] * len(grid) for _ in range(len(grid[0]))]

    for rowIdx in range(len(grid)):
        for colIdx in range(len(grid[rowIdx])):
            newGrid[colIdx][rowIdx] = grid[rowIdx][colIdx]

    return newGrid

# Creates a copy of the column-major grid as row-major. Essentially performs the reverse of TransposeGrid()
def InverseTransposeGrid(grid: list[list[int]]) -> list[list[int]]:
    newGrid = [[0] * len(grid) for _ in range(len(grid[0]))]

    for colIdx in range(len(grid)):
        for rowIdx in range(len(grid[colIdx])):
            newGrid[rowIdx][colIdx] = grid[colIdx][rowIdx]

    return newGrid

# Manually copies from srcGrid to dstGrid in-place
def CopyGrid(srcGrid: list[list[int]], dstGrid: list[list[int]]):
    for i in range(len(srcGrid)):
        for j in range(len(srcGrid[i])):
            dstGrid[i][j] = srcGrid[i][j]

def push_up(grid: list[list[int]]):
    """merge grid values upwards"""

    colMajorGrid = TransposeGrid(grid)
    for colIdx in range(len(colMajorGrid)):
        newCol = [num for num in colMajorGrid[colIdx] if num > 0]
        for i in range(len(newCol) - 1):
            if newCol[i] == newCol[i + 1]:
                newCol[i] *= 2
                newCol[i + 1] = 0

        newCol = [num for num in newCol if num > 0]
        colMajorGrid[colIdx] = newCol + ([0] * (len(colMajorGrid[colIdx]) - len(newCol)))

    CopyGrid(InverseTransposeGrid(colMajorGrid), grid)

def push_down(grid: list[list[int]]):
    """merge grid values downwards"""

    colMajorGrid = TransposeGrid(grid)
    for colIdx in range(len(colMajorGrid)):
        newCol = [num for num in colMajorGrid[colIdx] if num > 0]
        for i in range(len(newCol) - 1, 0, -1):
            if newCol[i] == newCol[i - 1]:
                newCol[i] *= 2
                newCol[i - 1] = 0

        newCol = [num for num in newCol if num > 0]
        colMajorGrid[colIdx] = ([0] * (len(colMajorGrid[colIdx]) - len(newCol))) + newCol

    CopyGrid(InverseTransposeGrid(colMajorGrid), grid)

def push_left(grid: list[list[int]]):
    """merge grid values left"""

    for rowIdx in range(len(grid)):
        newRow = [num for num in grid[rowIdx] if num > 0]
        for i in range(len(newRow) - 1):
            if newRow[i] == newRow[i + 1]:
                newRow[i] *= 2
                newRow[i + 1] = 0

        newRow = [num for num in newRow if num > 0]
        grid[rowIdx] = newRow + ([0] * (len(grid[rowIdx]) - len(newRow)))

def push_right(grid: list[list[int]]):
    """merge grid values right"""

    for rowIdx in range(len(grid)):
        newRow = [num for num in grid[rowIdx] if num > 0]
        for i in range(len(newRow) - 1, 0, -1):
            if newRow[i] == newRow[i - 1]:
                newRow[i] *= 2
                newRow[i - 1] = 0

        newRow = [num for num in newRow if num > 0]
        grid[rowIdx] = ([0] * (len(grid[rowIdx]) - len(newRow))) + newRow
