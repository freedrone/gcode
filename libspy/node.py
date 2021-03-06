from collections import defaultdict
from math import sqrt
from concorde import Tsp


def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class Layer:
    def __init__(self):
        self.curvelist = []
        self.edgematrix = []
        self.didwarn = False

    def addCurve(self, curve):
        self.curvelist.append(curve)

    def hasCurves(self):
        if len(self.curvelist) > 0:
            return True
        else:
            return False

    def getCurves(self):
        return self.curvelist

    def fillEdgeMatrix(self):
        for j in range(2 * len(self.curvelist)):
            row = []
            for k in range(2 * len(self.curvelist)):
                row.append(0)
            self.edgematrix.append(row)

        for (j, c1) in enumerate(self.curvelist):
            for (k, c2) in enumerate(self.curvelist):
                if c1 is not c2:
                    for p1 in range(2):
                        for p2 in range(2):
                            self.edgematrix[2 * j + p1][2 * k + p2] = distance(c1.get_x(p1), c1.get_y(p1), c2.get_x(p2), c2.get_y(p2))
                else:  # create 0-weight edges between endpoints on a given curve
                    for p1 in range(2):
                        for p2 in range(2):
                            self.edgematrix[2 * j + p1][2 * k + p2] = 0

    def getEdgeMatrix(self):
        return self.edgematrix

    def minimizeCost(self, startpoint, layernum):
        x, y = startpoint
        mincost, best_start, best_path = float("inf"), 0, []

        if len(self.curvelist) > 1:
            tsp = Tsp(self.edgematrix, "layer" + str(layernum))
            tsp_path, tsp_cost = tsp.solve()

            for (k, c) in enumerate(self.curvelist):
                nodes = [2 * k, 2 * k + 1]  # list of node numbers on this curve
                indexes = [tsp_path.index(2 * k), tsp_path.index(2 * k + 1)]  # list of locations of these nodes on path

                for (i, n) in enumerate(nodes):
                    # when picking a start point, we have to proceed to the end of the SFC first
                    # figure out which direction we have to traverse the TSP loop then
                    if (indexes[i] + 1) % len(tsp_path) == indexes[1 - i]:  # is other endpoint ahead of me in path?
                        forward = True
                        end = tsp_path[indexes[i] - 1]  # remove link behind me
                    elif (indexes[i] - 1) % len(tsp_path) == indexes[1 - i]:
                        forward = False
                        end = tsp_path[(indexes[i] + 1) % len(tsp_path)]  # remove link ahead of me
                    elif not self.didwarn:
                        self.didwarn = True
                        print("WARNING: Invalid path generated by Concorde on layer", layernum, ". Reported path cost will be a lower bound on gcode output.")

                    cost = tsp_cost - self.edgematrix[n][end]
                    d = distance(x, y, c.get_x(i), c.get_y(i))
                    if cost + d < mincost:
                        mincost, best_start, go_forward = cost + d, indexes[i], forward

            if go_forward:
                best_path = tsp_path[best_start:] + tsp_path[0:best_start]
            else:
                best_path = list(reversed(tsp_path[0:best_start + 1])) + list(reversed(tsp_path[best_start + 1:]))

        # no need for TSP if there is only one node on this layer - just pick which end to start at
        elif len(self.curvelist) == 1:
            d1 = distance(x, y, self.curvelist[0].get_x(0), self.curvelist[0].get_y(0))
            d2 = distance(x, y, self.curvelist[0].get_x(1), self.curvelist[0].get_y(1))
            if d1 < d2:
                mincost, best_path = d1, [0, 1]
            else:
                mincost, best_path = d2, [1, 0]

        curve, end = (best_path[-1] // 2), (best_path[-1] % 2)  # start point of last node on path for this layer
        endpoint = (self.curvelist[curve].get_x(end), self.curvelist[curve].get_y(end))

        return mincost, best_path, endpoint


class Curve:
    def __init__(self, xstart, ystart, xend, yend, number, startline, endline):
        self.x1 = xstart
        self.x2 = xend
        self.y1 = ystart
        self.y2 = yend
        self.index = number
        self.startline = startline
        self.endline = endline

    def get_x(self, point_0_or_1):
        if point_0_or_1 == 0:
            return self.x1
        elif point_0_or_1 == 1:
            return self.x2
        else:
            return 0

    def get_y(self, point_0_or_1):
        if point_0_or_1 == 0:
            return self.y1
        elif point_0_or_1 == 1:
            return self.y2
        else:
            return 0

    def get_startline(self):
        return self.startline

    def get_endline(self):
        return self.endline

    def print_node(self):
        print(self.index, self.startline, self.endline)
