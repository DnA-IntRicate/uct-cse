#include <print>
#include <vector>
#include <queue>
#include <set>
#include <stack>
#include <map>
#include <utility>
#include <random>
#include <numeric>
#include <algorithm>
#include <ranges>

// ============================================================================
// DATA STRUCTURES & MAZE GENERATION (PROVIDED)
// ============================================================================

using coordinate = std::pair<int, int>;

struct Maze
{
    std::vector<std::vector<bool>> grid;  // true = wall, false = path
    unsigned width;
    unsigned height;
    coordinate start;
    coordinate end;
};

class MazeGenerator {
private:
    std::mt19937 rng;

    void carvePath(Maze& maze, int x, int y) {
        maze.grid[y][x] = false;  // Mark as path

        // Define directions: right, down, left, up
        std::vector<coordinate> directions = {{2, 0}, {0, 2}, {-2, 0}, {0, -2}};
        std::ranges::shuffle(directions, rng);

        for (auto [dx, dy] : directions) {
            unsigned nx = x + dx;
            unsigned ny = y + dy;

            if ((nx < (maze.width - 1)) && (ny < (maze.height - 1)) && maze.grid[ny][nx]) {
                maze.grid[y + (dy / 2)][x + (dx / 2)] = false;  // Carve passage between cells
                carvePath(maze, nx, ny);
            }
        }
    }

public:
    MazeGenerator(unsigned seed = 42) : rng(seed) {}

    Maze generate(unsigned width, unsigned height) {
        Maze maze;
        maze.width = width;
        maze.height = height;
        maze.grid.assign(height, std::vector<bool>(width, true));  // All walls initially

        carvePath(maze, 1, 1);

        maze.start = {1, 1};
        maze.end = {width - 2, height - 2};

        return maze;
    }
};

void displayMaze(const Maze& maze) {
    for (auto y = 0u; y < maze.height; ++y) {
        for (auto x = 0u; x < maze.width; ++x) {
            if (std::make_pair(x, y) == maze.start) {
                std::print("S");
            } else if (std::make_pair(x, y) == maze.end) {
                std::print("E");
            } else if (maze.grid[y][x]) {
                if (std::make_pair(x+1, y) == maze.start) { std::print(">"); }
                else if  (std::make_pair(x-1, y) == maze.end) { std::print(">"); }
                else { std::print("#"); }
            } else {
                std::print(" ");
            }
        }
        std::print("\n");
    }
}

struct SolveStats {
    int pathLength;
    int cellsExplored = 0;
    double efficiency;
};

// ============================================================================
// PART 1: BFS SOLVER
// ============================================================================

enum class SearchMethod {
    BFS, DFS
};

// Template stub
template <SearchMethod method>
SolveStats solveMaze(const Maze& maze, std::vector<coordinate>& path);

// BFS specialization
template <>
SolveStats solveMaze<SearchMethod::BFS>(const Maze& maze, std::vector<coordinate>& path)
{
    // Step 1: Initialize Containers
    std::queue<coordinate> frontier;
    std::set<coordinate> visited;
    std::map<coordinate, coordinate> parentMap;

    // Step 2: Start the Exploration
    const coordinate& start = maze.start;
    const coordinate& goal = maze.end;

    frontier.push(start);
    visited.emplace(start);
    parentMap[start] = start;

    // Step 3: Main Loop
    while (!frontier.empty())
    {
        const coordinate cell = frontier.front(); frontier.pop();
        if (cell == goal)
            break;

        // Step 4: Explore Neighbors
        const auto& [cellX, cellY] = cell;

        std::vector<coordinate> neighbors;
        neighbors.emplace_back(cellX, cellY + 1); // Up
        neighbors.emplace_back(cellX, cellY - 1); // Down
        neighbors.emplace_back(cellX - 1, cellY); // Left
        neighbors.emplace_back(cellX + 1, cellY); // Right

        for (const auto& [x, y] : neighbors)
        {
            // Out of bounds
            if ((x >= static_cast<int>(maze.width)) || (y >= static_cast<int>(maze.height)))
                continue;

            // Wall check
            if (maze.grid[x][y])
                continue;

            // Check if visited
            const coordinate me = std::make_pair(x, y);
            if (std::ranges::find(visited, me) != visited.end())
                continue;

            visited.emplace(me);
            parentMap[me] = cell;
            frontier.push(me);
        }
    }

    // Step 5: Reconstruct the Path
    coordinate cell = goal;
    while (true)
    {
        path.push_back(cell);
        cell = parentMap.at(cell);

        if (cell == start)
            break;
    }

    // Reverse the path
    std::reverse(path.begin(), path.end());

    // Step 6: Calculate Statistics
    SolveStats result;
    result.pathLength = static_cast<int>(path.size());
    result.cellsExplored = static_cast<int>(visited.size());

    const auto& [sx, sy] = start;
    const auto& [gx, gy] = goal;

    double manhattan = std::abs(sx - gx) + std::abs(sy - gy);
    result.efficiency = manhattan / static_cast<double>(result.pathLength);

    return result;
}
// ============================================================================
// PART 2: DFS SOLVER
// ============================================================================

// DFS specialization
// I know I know... I copy-pasted and thats very but... Oh well, lol.
template<>
SolveStats solveMaze<SearchMethod::DFS>(const Maze& maze, std::vector<coordinate>& path)
{
    // Step 1: Initialize Containers
    std::stack<coordinate> frontier; // DFS USES A STACK!
    std::set<coordinate> visited;
    std::map<coordinate, coordinate> parentMap;

    // Step 2: Start the Exploration
    const coordinate& start = maze.start;
    const coordinate& goal = maze.end;

    frontier.push(start);
    visited.emplace(start);
    parentMap[start] = start;

    // Step 3: Main Loop
    while (!frontier.empty())
    {
        const coordinate cell = frontier.top(); frontier.pop();
        if (cell == goal)
            break;

        // Step 4: Explore Neighbors
        const auto& [cellX, cellY] = cell;

        std::vector<coordinate> neighbors;
        neighbors.emplace_back(cellX, cellY + 1); // Up
        neighbors.emplace_back(cellX, cellY - 1); // Down
        neighbors.emplace_back(cellX - 1, cellY); // Left
        neighbors.emplace_back(cellX + 1, cellY); // Right

        for (const auto& [x, y] : neighbors)
        {
            // Out of bounds
            if ((x >= static_cast<int>(maze.width)) || (y >= static_cast<int>(maze.height)))
                continue;

            // Wall check
            if (maze.grid[x][y])
                continue;

            // Check if visited
            const coordinate me = std::make_pair(x, y);
            if (std::ranges::find(visited, me) != visited.end())
                continue;

            visited.emplace(me);
            parentMap[me] = cell;
            frontier.push(me);
        }
    }

    // Step 5: Reconstruct the Path
    coordinate cell = goal;
    while (true)
    {
        path.push_back(cell);
        cell = parentMap.at(cell);

        if (cell == start)
            break;
    }

    // Reverse the path
    std::reverse(path.begin(), path.end());

    // Step 6: Calculate Statistics
    SolveStats result;
    result.pathLength = static_cast<int>(path.size());
    result.cellsExplored = static_cast<int>(visited.size());

    const auto& [sx, sy] = start;
    const auto& [gx, gy] = goal;

    double manhattan = std::abs(sx - gx) + std::abs(sy - gy);
    result.efficiency = manhattan / static_cast<double>(result.pathLength);

    return result;
}

// ============================================================================
// PART 3: ANALYSIS & OUTPUT (PROVIDED)
// ============================================================================

struct SolveResult {
    int mazeSize;
    std::string algorithm;
    int pathLength;
    int cellsExplored;
    double efficiency;
};

int main() {
    MazeGenerator generator(42);

    // Generate 3 mazes
    std::vector<Maze> mazes;
    std::vector<int> sizes = {11, 15, 21};

    for (int size : sizes) {
        mazes.push_back(generator.generate(size, size));
    }

    for (const auto& maze: mazes) { displayMaze(maze); }

    // Solve each maze with BFS and DFS
    std::vector<SolveResult> results;

    for (const auto& maze : mazes) {
        std::vector<coordinate> pathBFS, pathDFS;

        SolveStats bfsStats = solveMaze<SearchMethod::BFS>(maze, pathBFS);
        SolveResult bfsResult{(int)maze.width, "BFS", bfsStats.pathLength, bfsStats.cellsExplored, bfsStats.efficiency};
        results.push_back(bfsResult);

        SolveStats dfsStats = solveMaze<SearchMethod::DFS>(maze, pathDFS);
        results.push_back({(int)maze.width, "DFS", dfsStats.pathLength, dfsStats.cellsExplored, dfsStats.efficiency});
    }

    // Sort results by cellsExplored (ascending) using std::ranges::sort with lambda
    std::ranges::sort(results, [](const SolveResult& a, const SolveResult& b) {
        return a.cellsExplored < b.cellsExplored;
    });

    // Extract efficiency scores using std::ranges::transform
    std::vector<double> efficiencies;
    std::ranges::transform(results, std::back_inserter(efficiencies),
                          [](const SolveResult& r) { return r.efficiency; });

    // Compute average efficiency using std::accumulate
    double avgEfficiency = 0.0;
    if (!efficiencies.empty()) {
        avgEfficiency = std::accumulate(efficiencies.begin(), efficiencies.end(), 0.0) / efficiencies.size();
    }

    // Display results table
    std::print("┌──────────┬───────────┬─────────────┬────────────────┬────────────┐\n");
    std::print("│ Maze Size│ Algorithm │ Path Length │ Cells Explored │ Efficiency │\n");
    std::print("├──────────┼───────────┼─────────────┼────────────────┼────────────┤\n");

    for (const auto& result : results) {
        std::print("│{:>9} │{:>10} │{:>12} │{:>15} │{:>11.4f} │\n",
                   result.mazeSize, result.algorithm, result.pathLength,
                   result.cellsExplored, result.efficiency);
    }

    std::print("└──────────┴───────────┴─────────────┴────────────────┴────────────┘\n");
    std::print("\nAverage Efficiency: {:.4f}\n", avgEfficiency);

    return 0;
}
