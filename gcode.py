from node import *

def isExtrusionCmd(words):
	if words[0] == "G1" and words[1][0] == "X":
		return True
	else:
		return False

class Gcode:
	header_end = 0
	layers = []
	zgcode = []

	def __init__(self, filename):
		infile = open(filename, 'r')
		self.lines = infile.readlines()
		infile.close()

	def parse(self):	
		xstart, ystart, istart = 0, 0, 0
		xlast, ylast, self.ilast = 0, 0, 0
		curve_index = 0
		current_layer = Layer()
		save_next_point = False
	
		for (i, line) in enumerate(self.lines):
			words = line.split()
			if len(words) > 0:
		
				# Handle motion commands to parse out points
				if isExtrusionCmd(words):
					xlast, ylast = float(words[1][1:]), float(words[2][1:])
					self.ilast = i
					if save_next_point:
						xstart, ystart, istart = xlast, ylast, i
						save_next_point = False
					if self.header_end == 0:
						self.header_end = i
		
				else:
					# there are some extra commands at the beginning that would 
					# cause this code to create curves that start and end at (0, 0)
					if xlast != 0 or ylast != 0:
						new_curve = Curve(xstart, ystart, xlast, ylast, curve_index, istart, self.ilast)
						current_layer.addCurve(new_curve)
						curve_index = curve_index + 1
						xstart, ystart, xlast, ylast = 0, 0, 0, 0
					save_next_point = True
			
				# Update by adding last layer
				if words[0] == "G1" and words[1][0] == "Z":
					# we are switching to a new layer, so add this layer's curve list to layers and reset/update
					# don't do anything if there is no data in this layer (probably extra initialization commands)
					if current_layer.hasCurves():
						self.layers.append(current_layer)
						current_layer = Layer()
						curve_index = 0
						self.zgcode.append(line)
	
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
			for j in xrange(0, len(path), 2):
				node = path[j]
				curve = curves[node / 2]
				if node % 2 == 0: # write this gcode in original order
					for l in range(curve.get_startline(), curve.get_endline() + 1):
						if isExtrusionCmd(self.lines[l].split()):
							outfile.write(self.lines[l])
				else: # must reverse gcode
					for l in range(curve.get_endline(), curve.get_startline() - 1, -1):
						if isExtrusionCmd(self.lines[l].split()):
							outfile.write(self.lines[l])
				outfile.write("G92 E0\n")
			if i < len(self.zgcode):
				outfile.write(self.zgcode[i])
	
		for l in range(self.ilast + 1, len(self.lines)):
			outfile.write(self.lines[l])
		
		outfile.close()

