import matplotlib.pyplot as plt
import matplotlib.animation as animation
from node import *
from gcode import *
from concorde import *
from math import sqrt


if __name__ == "__main__":
	gcode = Gcode('octopus_rectilinear_100fill_4perim.gcode')
	layers = gcode.parse()
	
	## Construct Graph ##
	## (calculate distances between nodes on each layer)

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
			tsp = Tsp(matrices[j], "layer" + str(j))		
			tsp_path, tsp_cost = tsp.solve()
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
	gcode.reorder('octopus_rectilinear_100fill_4perim_reordered.gcode')

				
				
