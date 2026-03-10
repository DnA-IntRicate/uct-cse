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

	def get_next_move(self, board, is_init=False): #must return src_row, src_col, dest_row, dest_col
		#TODO: complete
		return 0,0,0,0
