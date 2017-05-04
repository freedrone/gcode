import matplotlib.pyplot as plt
import matplotlib.animation as animation
from node import Node, distance
from tsp_gcode import tsp
from math import sqrt

if __name__ == "__main__":
	infile = open('star_concentric.gcode', 'r')
	outfile = open('star_concentric_reordered.gcode', 'w')
	gcode = infile.readlines()
	infile.close()
	
	header_end = 0
	xstart, ystart, istart = 0, 0, 0
	xlast, ylast, ilast = 0, 0, 0
	layers = []
	layer_index = 0
	node_index = 0
	current_layer = []
	save_next_point = False
	
	for (i, line) in enumerate(gcode):
		words = line.split()
		if len(words) > 0:
		
			# Handle motion commands to parse out points
			if words[0] == "G1" and words[1][0] == "X":
				xlast, ylast = float(words[1][1:]), float(words[2][1:])
				ilast = i
				if save_next_point:
					xstart, ystart = xlast, ylast
					save_next_point = False
				if header_end == 0:
					header_end = i + 1
		
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
					layers.append(current_layer)
					current_layer = []
					layer_index = layer_index + 1
					node_index = 0
	
	# add data from any incomplete layer
	if current_layer != []:
		layers.append(current_layer)

	infile.close()		

	## Construct Graph ##
	## (calculate distances between nodes on each layer)
	for (i, layer) in enumerate(layers):
		for n1 in layer:
			for n2 in layer:
				if n1 is not n2:
					n1.make_edges(n2)
	print "Found", i+1, "layers."
	
	## Original Path Cost ##
	## (sum of distances between end points in order)
	original_cost = 0	
	prev_end = (0, 0) 
	
	for (i, layer) in enumerate(layers):
		for node in layer:
			original_cost += distance(prev_end[0], prev_end[1], node.get_x(0), node.get_y(0))
			prev_end = (node.get_x(1), node.get_y(1))
			
	print "Original path cost from Gcode:", original_cost		
	
	## Greedy TSP Distance Minimization ##
	## (minimize distance between space filling curve endpoins)
	solutions = []
	solution_cost = 0
	prev_layer_end = (0, 0) # set this initially to extrusion start point before first layer
	
	for layer in layers:
		mincost, best_start, best_path = float("inf"), 0, []
		
		# run TSP from every possible start node to minimize path + distance between layers
		if len(layer) > 1:
			for (i, node) in enumerate(layer):
				cost, path = tsp(layer, i)
				_, point = path[0] # node is same as i
				d = distance(prev_layer_end[0], prev_layer_end[1], node.get_x(point), node.get_y(point))
				
				if cost + d < mincost:
					mincost, best_start, best_path = cost + d, i, path
					
		# no need for TSP if there is only one node on this layer - just pick which end to start at
		elif len(layer) == 1:
			d1 = distance(prev_layer_end[0], prev_layer_end[1], layer[0].get_x(0), layer[0].get_y(0))
			d2 = distance(prev_layer_end[0], prev_layer_end[1], layer[0].get_x(1), layer[0].get_y(1))
			if d1 < d2:
				mincost, best_path = d1, [(0, 0)] # layer starts at point 0 of node 0
			else:
				mincost, best_path = d2, [(0, 1)] # layer starts at point 1 of node 0
				
		solutions.append((mincost, best_path))
		solution_cost += mincost
		idx, point = best_path[-1] # start point of last node on path for this layer
		prev_layer_end = (layer[idx].get_x(1 - point), layer[idx].get_y(1 - point))
	
	print "New path cost from solver:", solution_cost
	
	## Reorder/Rewrite Gcode File ##

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
	
	outfile.close()
				
				