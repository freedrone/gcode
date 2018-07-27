from libspy.node import distance
from libspy.gcode import Gcode
from time import time
import sys

if len(sys.argv) == 1:
    print("Usage: reorder-gcode.py <filename-no-extension>")

else:
    infile = sys.argv[1] + '.gcode'
    outfile = sys.argv[1] + '_reordered.gcode'

    gcode = Gcode(infile)
    layers = gcode.parse()
    print("\nFound", len(layers), "layers.")

    ## Construct Graph ##
    ## (calculate distances between curve endpoints on each layer)
    curvecounts = []
    for (i, layer) in enumerate(layers):
        curvecounts.append(len(layer.getCurves()))
        layer.fillEdgeMatrix()

    print("Curve count stats (curves/layer):")
    print("Min:", min(curvecounts), "Max:", max(curvecounts), "Avg:", sum(curvecounts) / len(curvecounts))

    ## Original Path Cost ##
    ## (sum of distances between end points in order)
    original_cost = 0
    endpoint = (0, 0)  # extrusion start point

    for (i, layer) in enumerate(layers):
        for c in layer.getCurves():
            original_cost += distance(endpoint[0], endpoint[1], c.get_x(0), c.get_y(0))
            endpoint = (c.get_x(1), c.get_y(1))

    print("\nOriginal path cost from Gcode:", original_cost)

    ## Greedy TSP Distance Minimization ##
    ## (minimize distance between space filling curve endpoins)
    solutions = []
    solution_cost = 0
    endpoint = (0, 0)  # set this initially to extrusion start point before first layer

    starttime = time()

    for (j, layer) in enumerate(layers):
        mincost, best_path, endpoint = layer.minimizeCost(endpoint, j)  # this will call into TSP solver
        solutions.append((mincost, best_path))
        solution_cost += mincost

    print("New path cost from solver:", solution_cost)
    print("Execution time:", time() - starttime, "seconds.")

    ## Reorder/Rewrite Gcode File ##
    gcode.reorder(outfile, solutions)

    print("New Gcode written to:", outfile)
