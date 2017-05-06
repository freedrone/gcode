import matplotlib.pyplot as plt
import matplotlib.animation as animation
from node import Node, distance
from tsp_gcode import tsp
from math import sqrt
import subprocess

def createTspFile(matrix, filename):
	tspfile = open(filename, 'w')
	tspfile.write('NAME: layer\n')
	tspfile.write('TYPE: TSP\n')
	tspfile.write('DIMENSION: ' + str(len(matrix)) +'\n')
	tspfile.write('EDGE_WEIGHT_TYPE: EXPLICIT\n')
	tspfile.write('EDGE_WEIGHT_FORMAT: FULL_MATRIX\n')
	tspfile.write('EDGE_WEIGHT_SECTION\n')
	'''tspfile.write(str(2 * len(layer)) + ' ' + str(edgecount) + '\n')
	for (i, node) in enumerate(layer):
		tspfile.write(str(2*i) + ' ' + str(2*i + 1) + ' 0\n') # there is no cost to move from one end of SFC to the other
		for point in range(2):
			edges = node.get_edges(point)
			for (d, j, p) in edges:
				if i < j:
					tspfile.write(str(2*i + point) + ' ' + str(2*j + p) + ' ' + str(d*100) + '\n')'''

	for row in matrix:
		for item in row:
			tspfile.write(str(item) + ' ')
		tspfile.write('\n')
	tspfile.write('EOF\n')
	tspfile.close()

def readSolutionFile(filename):
	solution = open(filename, 'r')
	lines = solution.readlines()
	data = ""
	for line in lines[1:]:
		data = data + line
	nodestrings = data.split()
	path = [int(node) for node in nodestrings]
	return path

def runConcorde(infile, outfile):
	args = ['../concorde/TSP/concorde', '-x', '-m','-o', outfile, infile]
		
	try:
		concorde = subprocess.Popen(args)
	
	except OSError:
		print "Could not launch concorde."
		sys.exit(0)
		return

	concorde.wait()
	return readSolutionFile(outfile)

def getCost(path, matrix):
	cost = 0
	for (i, node) in enumerate(path[:-1]):
		cost = cost + matrix[node][path[i+1]]
	
	cost = cost + matrix[path[-1]][path[0]]
	return cost

if __name__ == "__main__":
	infile = open('octopus_rectilinear_100fill_4perim.gcode', 'r')
	outfile = open('octopus_rectilinear_100fill_4perim_reordered.gcode', 'w')
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
	#edgecount = []
	matrices = []
	for (i, layer) in enumerate(layers):
		#e = len(layer) # we have one "edge" for each implicit connection between endpoints of SPC
		
		edgematrix = []	
		for n1 in layer:
			row0, row1 = [], []
			for n2 in layer:
				row0 = row0 + [0, 0]
				row1 = row1 + [0, 0]
			edgematrix.append(row0)
			edgematrix.append(row1)
		
		for (j, n1) in enumerate(layer):
			#print j, n1.get_x(0), n1.get_y(0), n1.get_x(1), n1.get_y(1)
			for (k, n2) in enumerate(layer):
				if n1 is not n2:
					n1.make_edges(n2)
					for p1 in range(2):
						for p2 in range(2):
							edgematrix[2*j + p1][2*k + p2] = distance(n1.get_x(p1), n1.get_y(p1), n2.get_x(p2), n2.get_y(p2))
				else:
					for p1 in range(2):
						for p2 in range(2):
							edgematrix[2*j + p1][2*k + p2] = 0
			print len(layer)		
				#if j < k:
					#e = e + 4 # make_edges creates 4 edges combinations of 2 endpoints
		#edgecount.append(e)
		matrices.append(edgematrix)
	print "Found", len(layers), "layers."


	## Original Path Cost ##
	## (sum of distances between end points in order)
	original_cost = 0	
	prev_end = (0, 0) 
	
	for (i, layer) in enumerate(layers):
		for sfc in layer:
			original_cost += distance(prev_end[0], prev_end[1], sfc.get_x(0), sfc.get_y(0))
			prev_end = (sfc.get_x(1), sfc.get_y(1))
			
	print "Original path cost from Gcode:", original_cost

	## Greedy TSP Distance Minimization ##
	## (minimize distance between space filling curve endpoins)
	solutions = []
	solution_cost = 0
	prev_layer_end = (0, 0) # set this initially to extrusion start point before first layer
	
	for (j, layer) in enumerate(layers):
		mincost, best_start, best_path = float("inf"), 0, []
		
		if len(layer) > 1:
			createTspFile(matrices[j], "layer" + str(j) + ".tsp")
			tsp_path = runConcorde("layer" + str(j) + ".tsp", "layer" + str(j) + ".sol")
			tsp_cost = getCost(tsp_path, matrices[j])
			print tsp_cost, tsp_path

			for (k, sfc) in enumerate(layer):
				nodes = [2*k, 2*k + 1]
				indexes = [tsp_path.index(2*k), tsp_path.index(2*k + 1)]
				
				for (i, n) in enumerate(nodes):
					# when picking a start point, we have to proceed to the end of the SFC first
					# figure out which direction we have to traverse the TSP loop then
					if (i + 1) % len(tsp_path) == indexes[1 - i]: # figure out whether other endpoint is ahead of me in path
						forward = True						
						end = tsp_path[indexes[i]-1] # remove link behind me				
					else:
						forward = False
						end = tsp_path[(indexes[i]+1) % len(tsp_path)] # remove link ahead of me

					cost = tsp_cost - matrices[j][n][end]
					d = distance(prev_layer_end[0], prev_layer_end[1], sfc.get_x(i), sfc.get_y(i))
					if cost + d < mincost:
						mincost, best_start, go_forward = cost + d, indexes[i], forward

			if go_forward:
				best_path = tsp_path[best_start:] + tsp_path[0:best_start]
			else:
				best_path = list(reversed(tsp_path[0:best_start+1])) + list(reversed(tsp_path[best_start+1:]))
					
		# no need for TSP if there is only one node on this layer - just pick which end to start at
		elif len(layer) == 1:
			d1 = distance(prev_layer_end[0], prev_layer_end[1], layer[0].get_x(0), layer[0].get_y(0))
			d2 = distance(prev_layer_end[0], prev_layer_end[1], layer[0].get_x(1), layer[0].get_y(1))
			if d1 < d2:
				mincost, best_path = d1, [0, 1]
			else:
				mincost, best_path = d2, [1, 0]

		solutions.append((mincost, best_path))
		solution_cost += mincost
		idx, point = (best_path[-1] / 2), (best_path[-1] % 2) # start point of last node on path for this layer
		prev_layer_end = (layer[idx].get_x(point), layer[idx].get_y(point))
		
	
	print "New path cost from solver:", solution_cost
	print solutions
	
	## Reorder/Rewrite Gcode File ##
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
				
				
