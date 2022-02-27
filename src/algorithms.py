#!/usr/bin/env python3
import pygame
import sys
import time
from heapq import heappush, heappop
from collections import defaultdict
from constants import Colours


def _get_neighbours(pos):
    tl, t, tr = (pos[0] - 1, pos[1] - 1), (pos[0] - 1, pos[1]), (pos[0] - 1, pos[1] + 1)
    bl, b, br = (pos[0] + 1, pos[1] - 1), (pos[0] + 1, pos[1]), (pos[0] + 1, pos[1] + 1)
    l, r = (pos[0], pos[1] - 1), (pos[0], pos[1] + 1)

    return [t, b, l, r, tl, tr, bl, br]


class PriorityQueue:

    def __init__(self, iterable=[]):
        self.heap = []
        for value in iterable:
            heappush(self.heap, (0, value))

    def add(self, value, priority=0):
        heappush(self.heap, (priority, value))

    def pop(self):
        priority, value = heappop(self.heap)
        return value

    def __len__(self):
        return len(self.heap)


class Dijkstra:

    def __init__(self, screen, start_pos, end_pos, squares, grid, edited_squares):
        self.screen = screen
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.squares = squares
        self.grid = grid
        self.edited_squares = edited_squares
        self.delay = 0.003
        self.grid_size = len(grid)
        self.que = PriorityQueue()
        self.que.add(self.start_pos)
        self.closed_list = set()
        self.minimums = defaultdict(lambda: sys.maxsize)
        self.minimums[self.start_pos] = 0

    def find_path(self):
        while self.que:
            cur = self.que.pop()

            if cur in self.closed_list or self.grid[cur[0]][cur[1]] == sys.maxsize:
                continue
            elif cur == self.end_pos:
                self.follow_minimums()
                return self.minimums[cur], self.edited_squares
            else:
                self.closed_list.add(cur)
                if cur != self.start_pos:
                    pygame.draw.rect(self.screen, Colours.DARK_GREEN.value, self.squares[cur[0]][cur[1]])

            for n in _get_neighbours(cur):
                if n[0] < 0 or n[0] > self.grid_size - 1 or n[1] < 0 or n[1] > self.grid_size - 1:
                    continue
                elif n in self.closed_list or self.grid[n[0]][n[1]] == sys.maxsize:
                    continue
                else:
                    if n != self.end_pos and n != self.start_pos:
                        pygame.draw.rect(self.screen, Colours.LIGHT_GREEN.value, self.squares[n[0]][n[1]])
                        self.edited_squares.append(self.squares[n[0]][n[1]])

                    neighbour_dist = self.minimums[cur] + self.grid[n[0]][n[1]]

                    if neighbour_dist < self.minimums[n]:
                        self.minimums[n] = neighbour_dist
                        self.que.add(n, priority=neighbour_dist)

            pygame.display.update()
            time.sleep(self.delay)

        return 0, self.edited_squares

    def follow_minimums(self):
        cur = self.end_pos
        local_closed_list = []
        dist_to_start = sys.maxsize
        next_square = None

        while True:
            for n in _get_neighbours(cur):
                if n[0] < 0 or n[0] > self.grid_size - 1 or n[1] < 0 or n[1] > self.grid_size - 1:
                    continue
                elif n in local_closed_list:
                    continue
                elif n == self.start_pos:
                    pygame.draw.rect(self.screen, Colours.ORANGE.value, self.squares[cur[0]][cur[1]])
                    pygame.display.update()
                    return

                if self.minimums[n] < dist_to_start:
                    dist_to_start = self.minimums[n]
                    next_square = n

            if cur != self.end_pos:
                pygame.draw.rect(self.screen, Colours.ORANGE.value, self.squares[cur[0]][cur[1]])

            local_closed_list.append(cur)
            cur = next_square


class AStar:

    def __init__(self, screen, start_pos, end_pos, squares, grid, edited_squares):
        self.screen = screen
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.squares = squares
        self.grid = grid
        self.edited_squares = edited_squares
        self.delay = 0.003
        self.grid_size = len(grid)
        self.que = PriorityQueue()
        self.que.add(self.start_pos)
        self.closed_list = set()
        self.distance = {self.start_pos: 0}
        self.parents = dict()

    def find_path(self):
        while self.que:
            cur = self.que.pop()

            if cur in self.closed_list or self.grid[cur[0]][cur[1]] == sys.maxsize:
                continue
            elif cur == self.end_pos:
                self.follow_parents()
                return self.distance[cur], self.edited_squares
            else:
                self.closed_list.add(cur)
                if cur != self.start_pos:
                    pygame.draw.rect(self.screen, Colours.DARK_GREEN.value, self.squares[cur[0]][cur[1]])

            for n in _get_neighbours(cur):
                if n[0] < 0 or n[0] > self.grid_size - 1 or n[1] < 0 or n[1] > self.grid_size - 1:
                    continue
                elif n in self.closed_list or self.grid[n[0]][n[1]] == sys.maxsize:
                    continue
                else:
                    self.que.add(n, priority=self.distance[cur] + 1 + self.h_cost(n))

                if n not in self.distance or self.distance[cur] + 1 < self.distance[n]:
                    self.distance[n] = self.distance[cur] + 1
                    self.parents[n] = cur

                    if n != self.end_pos and n != self.start_pos:
                        pygame.draw.rect(self.screen, Colours.LIGHT_GREEN.value, self.squares[n[0]][n[1]])
                        self.edited_squares.append(self.squares[n[0]][n[1]])

            pygame.display.update()
            time.sleep(self.delay)

        return 0, self.edited_squares

    def h_cost(self, pos):
        # http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html
        dx = abs(pos[0] - self.end_pos[0])
        dy = abs(pos[1] - self.end_pos[1])
        d1 = d2 = 1

        return d1 * (dx + dy) + (d2 - 2 * d1) * min(dx, dy)

    def follow_parents(self):
        cur = self.parents[self.end_pos]

        while cur != self.start_pos:
            pygame.draw.rect(self.screen, Colours.ORANGE.value, self.squares[cur[0]][cur[1]])
            cur = self.parents[cur]

        pygame.display.update()
