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
		xlast, ylast, self.ilast = 0, 0, 0
		layer_index = 0
		curve_index = 0
		current_layer = Layer()
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
						new_curve = Curve(xstart, ystart, xlast, ylast, curve_index, istart, self.ilast)
						current_layer.addCurve(new_curve)
						curve_index = curve_index + 1
						xstart, ystart, xlast, ylast = 0, 0, 0, 0
						istart = ilast + 1
					save_next_point = True
			
				# Update by adding last layer
				if words[0] == "G1" and words[1][0] == "Z":
					# we are switching to a new layer, so add this layer's curve list to layers and reset/update
					# don't do anything if there is no data in this layer (probably extra initialization commands)
					if current_layer.hasCurves():
						self.layers.append(current_layer)
						current_layer = Layer()
						layer_index = layer_index + 1
						curve_index = 0
	
		# add data from any incomplete layer
		if current_layer.hasCurves():
			self.layers.append(current_layer)

		return self.layers

	def reorder(self, filename, solutions):
		outfile = open(filename, 'w')
		
		for l in range(0, self.header_end):
			outfile.write(self.lines[l])
	
		for (i, (_, path)) in enumerate(solutions):
			curves = self.layers[i].getCurves()
			for node in path:
				curve = curves[node / 2]
				if node % 2 == 0: # write this gcode in original order
					for l in range(max(self.header_end + 1, curve.get_startline()), curve.get_endline() + 1):
						outfile.write(self.lines[l])
				else: # must reverse gcode
					other_commands = True
					line = max(self.header_end + 1, curve.get_startline())
					while other_commands:
						words = self.lines[line].split()
						if words[0] == "G1" and words[1][0] == "X":
							other_commands = False
						else:
							outfile.write(self.lines[line])
							line = line + 1
					for l in range(curve.get_endline(), line - 1, -1):
						outfile.write(self.lines[l])
	
		for l in range(self.ilast + 1, len(self.lines)):
			outfile.write(self.lines[l])
		
		outfile.close()

