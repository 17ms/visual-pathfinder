#!/usr/bin/env python3
from email import message
import pygame, random, math
from queue import PriorityQueue
from pygame.locals import *
from collections import defaultdict
from tkinter import Tk, messagebox
from sys import maxsize
from time import sleep

WHITE = (255, 255, 255)
GRAY = (125, 125, 125)
BLACK = (35, 35, 35)
GREEN = (0, 204, 0)
DARK_GREEN = (0, 89, 0)
RED = (255, 0, 0)
ORANGE = (255, 69, 0)
BLUE = (52, 79, 235)
PURPLE = (103, 14, 227)

modes = {0: BLUE, 1: PURPLE, 2: BLACK, 3: WHITE}
algo = 0
algo_names = ["Dijkstra", "A*"]
edit_mode = -1
start_cell, end_cell = None, None
start_xy, end_xy = None, None
grid_size = 60
edited_squares = []
delay = 0.003


def dijkstra(screen, grid, start, end, squares):
    global edited_squares
    
    gh, gw = len(grid), len(grid[0])
    que = PriorityQueue()
    closed_list = set()
    que.add(start)
    minimums = defaultdict(lambda: maxsize)
    minimums[start] = 0

    while que:
        cur = que.pop()
        if cur in closed_list or grid[cur[0]][cur[1]] == maxsize:
            continue
        elif cur == end:
            follow_minimums(start, end, gw, gh, minimums, screen, squares)
            return minimums[cur]
        else:
            closed_list.add(cur)
            if cur != start:
                pygame.draw.rect(screen, DARK_GREEN, squares[cur[0]][cur[1]])

        for n in get_neighbours(cur):
            if n[0] < 0 or n[0] > gw-1:
                continue
            elif n[1] < 0 or n[1] > gh-1:
                continue
            elif n in closed_list or grid[n[0]][n[1]] == maxsize:
                continue
            else:
                if n != end and n != start:
                    pygame.draw.rect(screen, GREEN, squares[n[0]][n[1]])
                    edited_squares.append(squares[n[0]][n[1]])
                
                n_distance = minimums[cur]+grid[n[0]][n[1]]
                if n_distance < minimums[n]:
                    minimums[n] = n_distance
                    que.add(n, priority=n_distance)

        # update grid visuals
        pygame.display.update()
        sleep(delay)

    return 0


def follow_minimums(start, end, gw, gh, minimums, screen, squares):
    cur = end
    closed_list = []
    l = maxsize
    nxt = None

    while True:
        for n in get_neighbours(cur):
            if n[0] < 0 or n[0] > gw-1:
                continue
            elif n[1] < 0 or n[1] > gh-1:
                continue
            elif n in closed_list:
                continue
            elif n == start:
                pygame.draw.rect(screen, ORANGE, squares[cur[0]][cur[1]])
                pygame.display.update()
                return
        
            if minimums[n] < l:
                l = minimums[n]
                nxt = n

        if cur != end:
            pygame.draw.rect(screen, ORANGE, squares[cur[0]][cur[1]])

        closed_list.append(cur)
        cur = nxt


def a_star(screen, grid, start, end, squares):
    global edited_squares

    gh, gw = len(grid), len(grid[0])
    que = PriorityQueue()
    closed_list = set()
    que.add(start)
    distance = {start: 0}
    parents = dict()

    while que:
        cur = que.pop()
        if cur in closed_list or grid[cur[0]][cur[1]] == maxsize:
            continue
        elif cur == end:
            follow_parents(start, end, parents, screen, squares)
            return distance[cur]
        else:
            closed_list.add(cur)
            if cur != start:
                pygame.draw.rect(screen, DARK_GREEN, squares[cur[0]][cur[1]])

        for n in get_neighbours(cur):
            if n[0] < 0 or n[0] > gw-1:
                continue
            elif n[1] < 0 or n[1] > gh-1:
                continue
            elif n in closed_list or grid[n[0]][n[1]] == maxsize:
                continue
            else:
                que.add(n, priority=distance[cur]+1+h_cost(n, end))

            if n not in distance or distance[cur]+1 < distance[n]:
                distance[n] = distance[cur]+1
                parents[n] = cur
                if n != end and n != start:
                    pygame.draw.rect(screen, GREEN, squares[n[0]][n[1]])
                    edited_squares.append(squares[n[0]][n[1]])

        # update grid visuals
        pygame.display.update()
        sleep(delay)

    return 0


def get_neighbours(pos):
    tl, t, tr = (pos[0]-1, pos[1]-1), (pos[0]-1, pos[1]), (pos[0]-1, pos[1]+1)
    bl, b, br = (pos[0]+1, pos[1]-1), (pos[0]+1, pos[1]), (pos[0]+1, pos[1]+1)
    l, r = (pos[0], pos[1]-1), (pos[0], pos[1]+1)

    return [t, b, l, r, tl, tr, bl, br]


def h_cost(pos, end):
    # http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html
    dx = abs(pos[0]-end[0])
    dy = abs(pos[1]-end[1])
    d1, d2 = 1, 1

    return d1*(dx+dy) + (d2-2*d1) * min(dx, dy)


def follow_parents(start, end, parents, screen, squares):
    cur = parents[end]
    while cur != start:
        pygame.draw.rect(screen, ORANGE, squares[cur[0]][cur[1]])
        cur = parents[cur]
    pygame.display.update()


def setup_grid(grid_size, size, screen):
    margin = 1
    margin_removed = size - grid_size * margin
    node_size = round(margin_removed / grid_size)
    squares = []

    for r in range(grid_size):
        sl = []
        for c in range(grid_size):
            x = margin + c * (margin + node_size)
            y = margin + r * (margin + node_size)
            rect = pygame.Rect(x, y, node_size, node_size)
            pygame.draw.rect(screen, WHITE, rect)
            sl.append(rect)
        squares.append(sl)

    return [[1 for i in range(grid_size)] for ii in range(grid_size)], squares


def setup_buttons(screen):
    start_label = pygame.font.SysFont("Ubuntu", 15).render("Set Start", 1, WHITE)
    end_label = pygame.font.SysFont("Ubuntu", 15).render("Set End", 1, WHITE)
    obs_label = pygame.font.SysFont("Ubuntu", 15).render("Set Obs.", 1, WHITE)
    random_label = pygame.font.SysFont("Ubuntu", 15).render("Randomize", 1, WHITE)
    clear_label = pygame.font.SysFont("Ubuntu", 15).render("Clear (1)", 1, WHITE)
    clean_label = pygame.font.SysFont("Ubuntu", 15).render("Clean", 1, WHITE)
    reset_label = pygame.font.SysFont("Ubuntu", 15).render("Reset", 1, WHITE)
    switch_label = pygame.font.SysFont("Ubuntu", 15).render("Switch", 1, WHITE)
    findpath_label = pygame.font.SysFont("Ubuntu", 15).render("Find Path", 1, WHITE)

    labels = [start_label, end_label, obs_label, random_label, clear_label, clean_label, reset_label, switch_label, findpath_label]
    buttons = []
    margin = 3
    next = (2, 905)

    for l in labels:
        w, h = l.get_size()
        bg_button = pygame.Rect(next[0], next[1], w+8, h+4)
        pygame.draw.rect(screen, WHITE, bg_button, 1)
        buttons.append(bg_button)
        screen.blit(l, (next[0]+4, next[1]+2))
        next = (next[0]+w+8+margin, next[1])

    last_pos = (next[0]+8, next[1]+1)
    
    return buttons, last_pos


def mark_cell(screen, rect, grid, xy, mode):
    global modes, start_cell, end_cell, start_xy, end_xy

    if mode == 0:
        # start
        if start_cell:
            pygame.draw.rect(screen, WHITE, start_cell)
            pygame.draw.rect(screen, modes[mode], rect)
        else:
            pygame.draw.rect(screen, modes[mode], rect)
        start_cell = rect
        start_xy = xy
        if grid[xy[0]][xy[1]] == maxsize:
            grid[xy[0]][xy[1]] = 1
    elif mode == 1:
        # end
        if end_cell:
            pygame.draw.rect(screen, WHITE, end_cell)
            pygame.draw.rect(screen, modes[mode], rect)
        else:
            pygame.draw.rect(screen, modes[mode], rect)
        end_cell = rect
        end_xy = xy
        if grid[xy[0]][xy[1]] == maxsize:
            grid[xy[0]][xy[1]] = 1
    elif mode == 4:
        # clear
        pygame.draw.rect(screen, WHITE, rect)
        if rect == end_cell:
            end_cell, end_xy = None, None
        elif rect == start_cell:
            start_cell, start_xy = None, None
        elif grid[xy[0]][xy[1]] == maxsize:
            grid[xy[0]][xy[1]] = 1

    return grid


def paint_obstacle(screen, grid, squares):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if click[0] == True:
        for y, r in enumerate(squares):
            for x, s in enumerate(r):
                if s.collidepoint(mouse):
                    pygame.draw.rect(screen, BLACK, s)
                    grid[y][x] = maxsize

    return grid


def random_obstacles(screen, grid, squares):
    for y, r in enumerate(squares):
        for x, s in enumerate(r):
            if random.getrandbits(1):
                pygame.draw.rect(screen, BLACK, s)
                grid[y][x] = maxsize

    return grid


def reset_grid(screen, squares, grid_size):
    for r in squares:
        for s in r:
            pygame.draw.rect(screen, WHITE, s)

    return [[1 for i in range(grid_size)] for ii in range(grid_size)]


def algo_label_update(screen, pos, old):
    global algo, algo_names
    # write over old
    screen.fill((0, 0, 0), (pos[0], pos[1], 100, 30))
    old = algo_names[algo]
    label = pygame.font.SysFont("Ubuntu", 15).render(old, 1, WHITE)
    screen.blit(label, pos)
    
    return old


def display_result(distance):
    Tk().wm_withdraw()
    msg = f"Distance: {str(distance)}"
    messagebox.showinfo("Done", msg)


def display_error(msg):
    Tk().wm_withdraw()
    messagebox.showerror("Error", msg)


def main():
    global edit_mode, grid_size, edited_squares, algo
    global start_cell, end_cell, start_xy, end_xy

    pygame.init()
    size = 900
    screen = pygame.display.set_mode([size+1, size+30])
    pygame.display.set_caption("visual-pathfinder")
    clock = pygame.time.Clock()
    
    # visual elements
    screen.fill((0, 0, 0))
    grid, squares = setup_grid(grid_size, size, screen)
    buttons, last_pos = setup_buttons(screen)
    algo_label1 = pygame.font.SysFont("Ubuntu", 15).render("Algorithm: ", 1, WHITE)
    lw, lh = algo_label1.get_size()
    screen.blit(algo_label1, (last_pos[0], last_pos[1]))
    last_pos = (last_pos[0]+lw+4, last_pos[1])
    current_algo_name = algo_names[algo]
    current_algo_name = algo_label_update(screen, last_pos, current_algo_name)

    done = 0
    while not done:
        mouse = pygame.mouse.get_pos()

        if edit_mode == 2:
            grid = paint_obstacle(screen, grid, squares)
        
        for b in buttons:
            if b.collidepoint(mouse):
                pygame.draw.rect(screen, GRAY, b.copy(), 1)
            else:
                pygame.draw.rect(screen, WHITE, b.copy(), 1)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                done = 1

            elif e.type == pygame.MOUSEBUTTONDOWN:
                for i, b in enumerate(buttons):
                    if b.collidepoint(mouse):
                        if i == 3:
                            # randomize (+ clean & reset)
                            if edited_squares:
                                for s in edited_squares:
                                    pygame.draw.rect(screen, WHITE, s)
                                edited_squares = []
                            grid = reset_grid(screen, squares, grid_size)
                            start_cell, start_xy = None, None
                            end_cell, end_xy = None, None
                            grid = random_obstacles(screen, grid, squares)
                        elif i == 5:
                            # clean
                            if edited_squares:
                                for s in edited_squares:
                                    pygame.draw.rect(screen, WHITE, s)
                                edited_squares = []
                        elif i == 6:
                            # reset
                            grid = reset_grid(screen, squares, grid_size)
                            start_cell, start_xy = None, None
                            end_cell, end_xy = None, None
                        elif i == 7:
                            if algo == len(algo_names)-1:
                                algo = 0
                            else:
                                algo += 1
                            current_algo_name = algo_label_update(screen, last_pos, current_algo_name)
                        elif i == 8:
                            # algo
                            if start_cell and end_cell:
                                if algo == 0:
                                    result = dijkstra(screen, grid, start_xy, end_xy, squares)
                                elif algo == 1:
                                    result = a_star(screen, grid, start_xy, end_xy, squares)
                                if result:
                                    display_result(result)
                                else:
                                    display_error("No possible path.")
                            else:
                                display_error("Start or end not set.")

                        edit_mode = i

                # choose cell to edit
                for i, r in enumerate(squares):
                    for j, s in enumerate(r):
                        if s.collidepoint(mouse):
                            if edit_mode not in [-1, 5, 6, 8]:
                                grid = mark_cell(screen, s, grid, (i, j), edit_mode)
            
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()
