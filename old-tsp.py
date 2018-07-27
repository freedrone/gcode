# Chloe Fleming

# Originally implemented for:
# CS 519 HW #8, 11/14/16

# Modified for:
# ROB 534 Final Project, 3/7/17

from collections import defaultdict
from .node import Node


# input graph format: ([Node1, Node2, ...], index)
# output format: (mincost, list) where list is the order of nodes visited in optimal path with mincost
def tsp(nodes, first_node):
    cache = defaultdict(lambda: (-1, -1))

    # to save space and avoid set operations, I used a bitmap to encode which nodes
    # are/aren't included in the "set" visited
    visited = 0
    for i in range(len(nodes)):
        visited |= (1 << i)

    # try to find a solution starting at every node i that connects to 0
    # keep best of these solutions and add cost(i, 0)
    mincost, v, start = float("inf"), -1, -1
    adj_0 = nodes[first_node].get_edges(0) + nodes[first_node].get_edges(1)
    for (wi0, vi, starti) in adj_0:
        # print "checking", vi, wi0
        costi0, _, start = _tsp(visited, vi, starti, first_node, nodes, cache)
        # costi0 += wi0
        if costi0 < mincost:
            mincost, v, start = costi0, vi, starti

    if mincost < float("inf"):
        result = backtrace(visited, v, 1 - start, cache)
        # result.append(0)
        return (mincost, result)
    else:
        return (mincost, [])


def _tsp(visited, vi, starti, first_node, nodes, cache, level=0):
    if (visited, vi, starti) in cache:
        return cache[(visited, vi, starti)]

    # base case: if bitmap has only bit 0 set, it is the set containing 0
    if visited == 2 ** first_node:
        cache[(visited, vi, starti)] = 0, -1, -1
        return cache[(visited, vi, starti)]

    mincost, j, start = float("inf"), -1, -1
    remaining = visited - (2 ** vi)
    adj_i = nodes[vi].get_edges(1 - starti)
    for (wij, vj, startj) in adj_i:
        # print "|"*level,vj, wij, remaining
        if (remaining >> vj) & 1 == 1:  # make sure vj is in set
            # print "|"*level,"y"
            cost, _, _ = _tsp(remaining, vj, startj, first_node, nodes, cache, level + 1)
            cost += wij
            if cost < mincost:
                mincost, j, start = cost, vj, startj
    # else:
    # print "|"*level,"n"

    cache[(visited, vi, starti)] = (mincost, j, start)
    # print "|"*level,visited, mincost, vi, j
    return (mincost, j, start)


def backtrace(visited, vi, starti, cache):
    cost, lastv, startj = cache[(visited, vi, starti)]
    if lastv > -1:
        remaining = visited - (2 ** vi)
        list = backtrace(remaining, lastv, startj, cache)
    else:
        list = []

    list.append((vi, 1 - starti))
    return list
