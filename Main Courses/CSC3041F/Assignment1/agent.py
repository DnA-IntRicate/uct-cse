from random import choice
from board import RawChessBoard, ChessBoardGUI
from copy import deepcopy
from typing import Optional
import math


_MCTS_MAX_ITERS: int = 500
_MCTS_ROLLOUT_DEPTH: int = 50

# TODO: Impl me for the random agent
def _get_all_actions(uboard: RawChessBoard, color: str) -> list:
    actions = []
    pieces = uboard.get_playable_moves(color)

    for piece in pieces:
        #print(piece)
        src_row, src_col = piece["row"], piece["col"]

        match piece["piece"]:
            case "B": dests = uboard.get_bishop_moves(src_row, src_col)
            case "K": dests = uboard.get_king_moves(src_row, src_col)
            case "N": dests = uboard.get_knight_moves(src_row, src_col)
            case "P": dests = uboard.get_pawn_moves(src_row, src_col)
            case "Q": dests = uboard.get_queen_moves(src_row, src_col)
            case "R": dests = uboard.get_rook_moves(src_row, src_col)
            case _: dests = []

        for dest_row, dest_col in dests:
            actions.append((src_row, src_col, dest_row, dest_col))

    return actions


class MCTSNode:
    def __init__(
            self,
            uboard: RawChessBoard,
            color: str,
            parent: Optional['MCTSNode'] = None,
            action = None,
            avail_actions = None
    ):
        self.uboard = uboard
        self.color = color
        self.parent = parent
        self.action = action if action is not None else []
        self.avail_actions = avail_actions if avail_actions is not None else []
        self.children: list['MCTSNode'] = []
        self.visits: int = 0
        self.wins: float = 0.0

    def is_terminal(self):
        return self.uboard.is_terminal(self.color)


    def is_fully_expanded(self):
        return len(self.avail_actions) == 0


    def expand(self) -> 'MCTSNode':
        if not self.avail_actions:
            raise RuntimeError("MCTSNode.expand called with no available actions!")

        action = self.avail_actions.pop()
        src_row, src_col, dest_row, dest_col = action

        uboard_copy = deepcopy(self.uboard)
        uboard_copy.move_piece(self.color, src_row, src_col, dest_row, dest_col)

        # Check opponent's next move
        opp_color = "white" if self.color == "black" else "black"
        opp_actions = _get_all_actions(uboard_copy, opp_color)

        child = MCTSNode(
            uboard=uboard_copy,
            color=opp_color,
            parent=self,
            action=action,
            avail_actions=opp_actions.copy()
        )

        self.children.append(child)
        return child


    def best_child(self, c: float = 1.14) -> 'MCTSNode':
        if not self.children:
            raise RuntimeError("MCTSNode.best_child called on node with no children!")

        for child in self.children:
            if child.visits == 0:
                return child

        def ucb(child: 'MCTSNode') -> float:
            exploit = child.wins / child.visits
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb)


    def backpropagate(self, result: int):
        node = self
        while node is not None: # We could do this recursively but eh.
            node.visits += 1
            if node.color == "black":
                if result == -1:    # White won
                    node.wins += 1
                elif result == 0:   # Draw
                    node.wins += 0.5
            else: # node.color == "white" (Black just moved)
                if result == 1: # Black won
                    node.wins += 1
                elif result == 0:   # Draw
                    node.wins += 0.5

            node = node.parent

class MonteCarloChessAgent(object):
    def __init__(self, color, opponent):
        self.color = color
        self.opponent = opponent

    def get_next_move(self, board: ChessBoardGUI):
        uboard: RawChessBoard = board.uboard
        root_actions = _get_all_actions(uboard, self.color)

        root = MCTSNode(
            uboard=deepcopy(uboard),
            color=self.color,
            parent=None,
            action=None,
            avail_actions=root_actions.copy()
        )

        for _ in range(_MCTS_MAX_ITERS):
            node = root
            while not node.is_terminal() and node.is_fully_expanded() and node.children:
                node = node.best_child()

            if not node.is_terminal() and not node.is_fully_expanded():
                node = node.expand()

            res = self._rollout(node)
            node.backpropagate(res)

        # Return a randomly incase anything breaks so that we don't crash
        if not root.children:
            return choice(root_actions)

        best = max(root.children, key=lambda x: x.visits)
        return best.action # Must return src_row, src_col, dest_row, dest_col


    def _rollout(self, node: MCTSNode) -> int:
        uboard_copy = deepcopy(node.uboard)
        current_color = node.color

        moves = 0
        while not uboard_copy.is_terminal(current_color) and (moves < _MCTS_ROLLOUT_DEPTH):
            dests = _get_all_actions(uboard_copy, current_color)
            if not dests:
                break

            src_row, src_col, dest_row, dest_col = choice(dests)
            uboard_copy.move_piece(current_color, src_row, src_col, dest_row, dest_col)
            current_color = "white" if current_color == "black" else "black" # Switch player
            moves += 1

        return self._check_winner(uboard_copy)


    # Returns 1 if black wins, -1 if white, and 0 if neither.
    def _check_winner(self, uboard: RawChessBoard) -> int:
        res = uboard.find_king_in_checkmate() # Returns the color that lost
        if res is None:
            return 0

        return 1 if res == "white" else -1


class RandomChessAgent(object):
    def __init__(self, color):
        self.color = color


    def get_next_move(self, board: ChessBoardGUI, is_init: bool = False) -> tuple[int, int, int, int]:
        uboard: RawChessBoard = board.uboard
        color_playable_moves = uboard.get_playable_moves(self.color)

        # Only pawns and knights may be moved in the initial state
        if is_init:
            color_playable_moves = [m for m in color_playable_moves if m["piece"] in ["p", "n"]]

        piece = choice(color_playable_moves)
        src_row, src_col = piece["row"], piece["col"]

        moves: list = []
        match piece["piece"]:
            case "b": moves = uboard.get_bishop_moves(src_row, src_col)
            case "k": moves = uboard.get_king_moves(src_row, src_col)
            case "n": moves = uboard.get_knight_moves(src_row, src_col)
            case "p": moves = uboard.get_pawn_moves(src_row, src_col)
            case "q": moves = uboard.get_queen_moves(src_row, src_col)
            case "r": moves = uboard.get_rook_moves(src_row, src_col)

        if not moves:
            return self.get_next_move(board, is_init)

        dest_row, dest_col = choice(moves)
        return src_row, src_col, dest_row, dest_col
