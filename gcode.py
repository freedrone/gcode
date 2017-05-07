from node import *

class Gcode:
	header_end = 0
	layers = []

	def __init__(self, filename):
		infile = open(filename, 'r')
		self.lines = infile.readlines()
		infile.close()

	def parse(self):	
		xstart, ystart, istart = 0, 0, 0
		xlast, ylast, ilast = 0, 0, 0
		layer_index = 0
		node_index = 0
		current_layer = []
		save_next_point = False
	
		for (i, line) in enumerate(self.lines):
			words = line.split()
			if len(words) > 0:
		
				# Handle motion commands to parse out points
				if words[0] == "G1" and words[1][0] == "X":
					xlast, ylast = float(words[1][1:]), float(words[2][1:])
					ilast = i
					if save_next_point:
						xstart, ystart = xlast, ylast
						save_next_point = False
					if self.header_end == 0:
						self.header_end = i + 1
		
				# Handle breaks in extrusion (within or between layers)
				if (words[0] == "G92" and words[1] == "E0") or (words[0] == "G1" and words[1][0] == "Z"):
					# there are some extra commands at the beginning that would 
					# cause this code to create curves that start and end at (0, 0)
					if xlast != xstart or ylast != ystart:
						new_node = Node(xstart, ystart, xlast, ylast, node_index, istart, ilast)
						current_layer.append(new_node)
						node_index = node_index + 1
						xstart, ystart, xlast, ylast = 0, 0, 0, 0
						istart = ilast + 1
					save_next_point = True
			
				# Update by adding last layer
				if words[0] == "G1" and words[1][0] == "Z":
					# we are switching to a new layer, so add this layer's node list to layers and reset/update
					# don't do anything if there is no data in this layer (probably extra initialization commands)
					if current_layer != []:
						self.layers.append(current_layer)
						current_layer = []
						layer_index = layer_index + 1
						node_index = 0
	
		# add data from any incomplete layer
		if current_layer != []:
			self.layers.append(current_layer)

		return self.layers

	def reorder(self, filename):
		outfile = open(filename, 'w')
		'''
		for l in range(0, header_end):
			outfile.write(gcode[l])
	
		for (i, (_, path)) in enumerate(solutions):
			for (j, direction) in path:
				node = layers[i][j]
				if direction == 0:
					for l in range(max(header_end + 1, node.get_startline()), node.get_endline() + 1):
						outfile.write(gcode[l])
				else:
					other_commands = True
					line = max(header_end + 1, node.get_startline())
					while other_commands:
						words = gcode[line].split()
						if words[0] == "G1" and words[1][0] == "X":
							other_commands = False
						else:
							outfile.write(gcode[line])
							line = line + 1
					for l in range(node.get_endline(), line - 1, -1):
						outfile.write(gcode[l])
	
		for l in range(ilast + 1, len(gcode)):
			outfile.write(gcode[l])
		'''
		outfile.close()

