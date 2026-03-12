from random import choice
from board import RawChessBoard, ChessBoardGUI
import copy
import math

class MonteCarloChessAgent(object):
    def __init__(self, color, opponent):
        self.color = color
        self.opponent = opponent


    def get_next_move(self, board): #must return src_row, src_col, dest_row, dest_col
        #TODO: complete
        return 0,0,0,0


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
