import matplotlib.pyplot as plt
import matplotlib.animation as animation
from node import *
from gcode import *

if __name__ == "__main__":
	gcode = Gcode('octopus_rectilinear_100fill_4perim.gcode')
	layers = gcode.parse()
	print "Found", len(layers), "layers."	

	## Construct Graph ##
	## (calculate distances between curve endpoints on each layer)
	for (i, layer) in enumerate(layers):
		layer.fillEdgeMatrix()

	## Original Path Cost ##
	## (sum of distances between end points in order)
	original_cost = 0	
	endpoint = (0, 0) # extrusion start point
	
	for (i, layer) in enumerate(layers):
		for c in layer.getCurves():
			original_cost += distance(endpoint[0], endpoint[1], c.get_x(0), c.get_y(0))
			prev_end = (c.get_x(1), c.get_y(1))
			
	print "Original path cost from Gcode:", original_cost

	## Greedy TSP Distance Minimization ##
	## (minimize distance between space filling curve endpoins)
	solutions = []
	solution_cost = 0
	endpoint = (0, 0) # set this initially to extrusion start point before first layer
	
	for (j, layer) in enumerate(layers):
		mincost, best_path, endpoint = layer.minimizeCost(endpoint, j)
		solutions.append((mincost, best_path))
		solution_cost += mincost
		
	print "New path cost from solver:", solution_cost
	print solutions
	
	## Reorder/Rewrite Gcode File ##
	gcode.reorder('octopus_rectilinear_100fill_4perim_reordered.gcode', solutions)

				
				
