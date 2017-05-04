import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np

if __name__ == "__main__":
	file = open('star_concentric_reordered.gcode', 'r')
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

	def animate(i):
		global layer_index, point_index, xlist, ylist, segments
		
		if point_index >= len(xlist):
			segments.append(list(zip(xlist, ylist)))
			layer_index = layer_index + 1
			xlist = [xlist[-1]] + xlayers[layer_index]
			ylist = [ylist[-1]] + ylayers[layer_index]
			point_index = 0
		
		segment = list(zip(xlist[:point_index+1], ylist[:point_index+1]))
		line.set_segments(segments+[segment])
		#line.set_xdata(xlist[:point_index+1])  # update the data
		#line.set_ydata(ylist[:point_index+1])  # update the data
		point_index = point_index + 1
		
		return line,		

	# Set up formatting for the movie files
	Writer = animation.writers['ffmpeg']
	writer = Writer(fps=25, metadata=dict(artist='Me'), bitrate=1800)	
		
	fig, ax = plt.subplots()
	plt.ylim((0,200))
	plt.xlim((0,200))
	
	line = LineCollection([], cmap=plt.cm.rainbow, array=np.array([0.1, 9.4, 3.8, 2.0]))
	ax.add_collection(line)
	
	ani = animation.FuncAnimation(fig, animate, frames=total_length, interval=5, blit=True)
	print "Saving animation..."
	#ani.save('star_concentric_reordered.mp4', writer=writer)
	print "Done."
	plt.show()