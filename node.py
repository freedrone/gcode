from collections import defaultdict
from math import sqrt

def distance(x1, y1, x2, y2):
	return sqrt((x2 - x1)**2 + (y2 - y1)**2)

class Node:
	x1, x2, y1, y2 = 0, 0, 0, 0
	startline, endline = 0, 0
	index = 0
	edge_list = defaultdict(list)
	
	def __init__(self, xstart, ystart, xend, yend, number, startline, endline):
		self.x1 = xstart
		self.x2 = xend
		self.y1 = ystart
		self.y2 = yend
		self.index = number
		self.startline = startline
		self.endline = endline
		self.edge_list = defaultdict(list)
		
	def make_edges(self, other):
		self.edge_list[0].append((distance(other.x1, other.y1, self.x1, self.y1), other.index, 0));
		self.edge_list[0].append((distance(other.x2, other.y2, self.x1, self.y1), other.index, 1));
		self.edge_list[1].append((distance(other.x1, other.y1, self.x2, self.y2), other.index, 0));
		self.edge_list[1].append((distance(other.x2, other.y2, self.x2, self.y2), other.index, 1));
		
	def get_edges(self, end_index):
		return self.edge_list[end_index]
		
	def get_x(self, point_0_or_1):
		if point_0_or_1 == 0:
			return self.x1
		elif point_0_or_1 == 1:
			return self.x2
		else:
			return 0
			
	def get_y(self, point_0_or_1):
		if point_0_or_1 == 0:
			return self.y1
		elif point_0_or_1 == 1:
			return self.y2
		else:
			return 0

	def get_startline(self):
		return self.startline
			
	def get_endline(self):
		return self.endline
		
	def print_node(self):
		print self.index, self.startline, self.endline
		
	def print_edges(self):
		for end in self.edge_list:
			for edge in self.edge_list[end]:
				print edge
		print "\n\n"
		