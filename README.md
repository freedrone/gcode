# gcode

This project includes a set of Python scripts for reordering fabrication toolpaths to reduce travel distance between endpoints of subsequent space-filling curves. The scripts parse Gcode (sliced object models for 3D printing), interpret the instructions as a graph, and apply a TSP solver (Concorde) to find paths that are selected with a greedy approach to minimization.
