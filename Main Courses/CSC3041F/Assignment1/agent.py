from random import choice
from board import RawChessBoard, ChessBoardGUI
from copy import deepcopy
from typing import Optional
import math


class MCTSNode:
    def __init__(
            self,
            uboard: RawChessBoard,
            color: str,
            parent: Optional['MCTSNode'] = None,
            action: Optional[tuple[int, int, int, int]] = None,
            avail_actions: list[tuple[int, int, int, int]] = []
    ):
        self.uboard = uboard
        self.color = color
        self.parent = parent
        self.action = action
        self.avail_actions = avail_actions
        self.children: list['MCTSNode'] = []
        self.visits: int = 0
        self.wins: float = 0.0

    def is_terminal(self):
        return self.uboard.is_terminal(self.color)

    def is_fully_expanded(self):
        return len(self.avail_actions) == 0

    def expand(self) -> 'MCTSNode':
        action = self.avail_actions.pop()
        src_row, src_col, dest_row, dest_col = action

        uboard_copy = deepcopy(self.uboard)
        uboard_copy.move_piece(self.color, src_row, src_col, dest_row, dest_col)

        # Check opponent's next move
        opp_color = "white" if self.color == "black" else "black"
        opp_actions = uboard_copy.get_playable_moves(opp_color)

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
        while node is not None: # We could do this recurisvely but eh.
            node.visits += 1
            if node.color == "black":
                node.wins += result
            else:
                node.wins -= result

            node = node.parent

class MonteCarloChessAgent(object):
    def __init__(self, color, opponent):
        self.color = color
        self.opponent = opponent


    def get_next_move(self, board: ChessBoardGUI):
        uboard: RawChessBoard = board.uboard
        color_playable_moves = uboard.get_playable_moves(self.color)

        # MCTS rough impl
        visited = []
        # tree: dict[]
        # s0 = something...

        # UCB1 formula:
        # UCB1 = Vi + C * sqrt(ln(N) / ni) ; C = 1.14
        # NOTE: We'll need to compute the argmax(UCB1) for all child nodes in each iteration, the argmax becomes
        # the next node we visit

        return 0,0,0,0 #must return src_row, src_col, dest_row, dest_col


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
