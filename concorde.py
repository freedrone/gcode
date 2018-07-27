from subprocess import Popen
import os


class Tsp:
    log_file = 'concorde.log'

    def __init__(self, edgematrix, name):
        self.edgematrix = edgematrix
        self.name = name
        self.tsplib_file = name + '.tsp'
        self.solution_file = name + '.sol'

    def solve(self):
        self.createTsplib()
        self.runConcorde()
        path = self.readSolution()
        os.remove(self.tsplib_file)
        os.remove(self.solution_file)
        return path, self.getCost(path)

    def createTsplib(self):
        tspfile = open(self.tsplib_file, 'w')
        tspfile.write('NAME: ' + self.name + '\n')
        tspfile.write('TYPE: TSP\n')
        tspfile.write('DIMENSION: ' + str(len(self.edgematrix)) + '\n')
        tspfile.write('EDGE_WEIGHT_TYPE: EXPLICIT\n')
        tspfile.write('EDGE_WEIGHT_FORMAT: FULL_MATRIX\n')
        tspfile.write('EDGE_WEIGHT_SECTION\n')

        for row in self.edgematrix:
            for item in row:
                tspfile.write(str(int(round(item * 100))) + ' ')
            tspfile.write('\n')
        tspfile.write('EOF\n')
        tspfile.close()

    def runConcorde(self):
        args = ['./libs/concorde/TSP/concorde', '-x', '-m', '-o', self.solution_file, self.tsplib_file]

        try:
            log = open(self.log_file, 'a')
            subproc = Popen(args, stdout=log, stderr=log)

        except OSError:
            print("Could not launch concorde.")
            exit(0)
            return

        subproc.wait()
        log.close()

    def readSolution(self):
        solution = open(self.solution_file, 'r')
        lines = solution.readlines()
        data = ""
        for line in lines[1:]:
            data = data + line
        nodestrings = data.split()
        path = [int(node) for node in nodestrings]
        return path

    def getCost(self, path):
        cost = 0
        for (i, node) in enumerate(path[:-1]):
            cost = cost + self.edgematrix[node][path[i + 1]]

        cost = cost + self.edgematrix[path[-1]][path[0]]
        return cost
