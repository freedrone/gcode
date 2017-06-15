import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import sys

if len(sys.argv) != 2:
	print "Usage: animate-gcode.py <filename-no-extension>"

else:
	infile = sys.argv[1] + '.gcode'
	file = open(infile, 'r')
	xlayers, ylayers = [], []
	xlist, ylist = [], []
	xprev, yprev = 0, 0
	e0x, e0y = [], []
	total_length = 0
	
	for (i, line) in enumerate(file):
		words = line.split()
		if len(words) > 0:
			if words[0] == "G1" and words[1][0] == "X":
				x, y = float(words[1][1:]), float(words[2][1:])
				xlist.append(x)
				ylist.append(y)
				xprev, yprev = x, y
				total_length = total_length + 1
				
			if words[0] == "G92" and words[1] == "E0":
				e0x.append(xprev)
				e0y.append(yprev)
				
			# stop after the first Z command not related to setup
			if words[0] == "G1" and words[1][0] == "Z":
				if xlist != [] and ylist != []:
					xlayers.append(xlist)
					ylayers.append(ylist)
					xlist, ylist = [], []

	xlayers.append(xlist)
	ylayers.append(ylist)
	
	layer_index = 0
	point_index = 0
	segments = []
	xlist = xlayers[layer_index]
	ylist = ylayers[layer_index]
		
	fig, ax = plt.subplots()
	plt.ylim((50,150))
	plt.xlim((50,150))
	plt.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
	plt.tick_params(axis='y', which='both', left='off', right='off', labelleft='off')
	ax.set_aspect('equal')
	plt.plot(xlayers[10], ylayers[10], color='blue')
	#plt.plot(e0x, e0y, color='black', marker='.', linestyle=' ')
	plt.show()
