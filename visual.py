#!/usr/bin/env python
import pygame
from pygame.locals import *
from collections import defaultdict
from sys import maxsize

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
edit_mode = -1
start_cell, end_cell = None, None
start_xy, end_xy = None, None
grid_size = 60
edited_squares = []


def dijkstra(screen, grid, start, end, squares):
    global edited_squares
    
    gh, gw = len(grid), len(grid[0])
    heap_que = defaultdict(tuple)
    heap_que[start] = 0
    visited = set()
    minimums = defaultdict(lambda: maxsize)

    while heap_que:
        distance = min(heap_que.values())
        cur = list(heap_que.keys())[list(heap_que.values()).index(distance)]
        heap_que.pop(cur)

        if cur == end:
            print(f"distance: {str(distance)}")
            break
        elif cur in visited:
            continue
        else:
            visited.add(cur)
            if cur != start:
                pygame.draw.rect(screen, DARK_GREEN, squares[cur[0]][cur[1]])
                edited_squares.append(squares[cur[0]][cur[1]])

        # calculate weights for neighbours
        t, b = (cur[0]-1, cur[1]), (cur[0]+1, cur[1])
        l, r = (cur[0], cur[1]-1), (cur[0], cur[1]+1)
        
        for n in [t, b, l, r]:
            if n[0] < 0 or n[0] > gw-1:
                continue
            elif n[1] < 0 or n[1] > gh-1:
                continue
            elif n in visited:
                continue

            if n != end and grid[n[0]][n[1]] == 1:
                pygame.draw.rect(screen, GREEN, squares[n[0]][n[1]])
                edited_squares.append(squares[n[0]][n[1]])

            n_weigh = grid[n[0]][n[1]]
            n_distance = distance + n_weigh
            if n_distance < minimums[n]:
                minimums[n] = n_distance
                heap_que[n] = n_distance

            # update grid visuals
            pygame.display.update()

    # backtrack & visualize the path
    cur = end
    visited = []
    lowest = maxsize
    next = None

    while True:
        t, b = (cur[0]-1, cur[1]), (cur[0]+1, cur[1])
        l, r = (cur[0], cur[1]-1), (cur[0], cur[1]+1)

        for n in [t, b, l, r]:
            if gw-1 < n[0] < 0 or gh-1 < n[1] < 0:
                continue
            elif n in visited:
                continue
            elif n == start:
                pygame.draw.rect(screen, ORANGE, squares[cur[0]][cur[1]])
                return

            if minimums[n] < lowest:
                lowest = minimums[n]
                next = n

        if cur != end: 
            pygame.draw.rect(screen, ORANGE, squares[cur[0]][cur[1]])

        visited.append(cur)

        if next is None:
            print("no possible path found")
            return

        cur = next


def a_star(grid, start, end):
    # TODO add a*
    pass


def setup_grid(grid_size, size, screen):
    margin = 2
    margin_removed = size - (grid_size + 1) * margin
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
    buttons = [pygame.Rect(5, 605, 30, 15),
               pygame.Rect(40, 605, 30, 15),
               pygame.Rect(75, 605, 30, 15),
               pygame.Rect(110, 605, 30, 15),
               pygame.Rect(145, 605, 45, 15),
               pygame.Rect(535, 605, 60, 15)]
    
    for b in buttons:
        pygame.draw.rect(screen, WHITE, b)

    start_label = pygame.font.SysFont("Ubuntu", 11).render("Start", 1, BLACK)
    end_label = pygame.font.SysFont("Ubuntu", 11).render("End", 1, BLACK)
    obs_label = pygame.font.SysFont("Ubuntu", 11).render("Obs.", 1, BLACK)
    clear_label = pygame.font.SysFont("Ubuntu", 11).render("Clear", 1, BLACK)
    clear_all_label = pygame.font.SysFont("Ubuntu", 11).render("Clear all", 1, BLACK)
    begin_label = pygame.font.SysFont("Ubuntu", 11).render("Begin algo", 1, BLACK)
    screen.blit(start_label, (8, 607))
    screen.blit(end_label, (45, 607))
    screen.blit(obs_label, (78, 607))
    screen.blit(clear_label, (112, 607))
    screen.blit(clear_all_label, (147, 607))
    screen.blit(begin_label, (540, 607))

    return buttons


def mark_cell(screen, rect, grid, xy, mode):
    global modes, start_cell, end_cell, start_xy, end_xy

    match mode:
        case 0:
            # set start (update grid)
            if start_cell:
                pygame.draw.rect(screen, WHITE, start_cell)
                pygame.draw.rect(screen, modes[mode], rect)
            else:
                pygame.draw.rect(screen, modes[mode], rect)
            start_cell = rect
            start_xy = xy
        case 1:
            # set end (update grid)
            if end_cell:
                pygame.draw.rect(screen, WHITE, end_cell)
                pygame.draw.rect(screen, modes[mode], rect)
            else:
                pygame.draw.rect(screen, modes[mode], rect)
            end_cell = rect
            end_xy = xy
        case 2:
            # set obstacle (update grid)
            pygame.draw.rect(screen, BLACK, rect)
            grid[xy[0]][xy[1]] = maxsize
        case 3:
            # clear cell
            pygame.draw.rect(screen, WHITE, rect)
            if rect == end_cell:
                end_cell, end_xy = None, None
            elif rect == start_cell:
                start_cell, start_xy = None, None
            elif grid[xy[0]][xy[1]] == maxsize:
                grid[xy[0]][xy[1]] = 1

    return grid


def reset_grid(screen, squares, grid_size):
    for r in squares:
        for s in r:
            pygame.draw.rect(screen, WHITE, s)

    return [[1 for i in range(grid_size)] for ii in range(grid_size)]


def main():
    global edit_mode, grid_size, edited_squares
    global start_cell, end_cell, start_xy, end_xy

    pygame.init()
    size = 600
    screen = pygame.display.set_mode([size, size+25])
    pygame.display.set_caption("visual-pathfinder")
    clock = pygame.time.Clock()
    
    # visual elements
    screen.fill((0, 0, 0))
    grid, squares = setup_grid(grid_size, size, screen)
    buttons = setup_buttons(screen)
       
    done = 0
    while not done:
        mouse = pygame.mouse.get_pos()
        
        for b in buttons:
            if b.collidepoint(mouse):
                pygame.draw.rect(screen, GRAY, b.copy(), 1)
            else:
                pygame.draw.rect(screen, WHITE, b.copy(), 1)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                done = 1

            elif e.type == pygame.MOUSEBUTTONDOWN:
                # clean the grid
                if edited_squares:
                    for s in edited_squares:
                        pygame.draw.rect(screen, WHITE, s)
                    edited_squares = []

                # choose mode / start algo
                for i, b in enumerate(buttons):
                    if b.collidepoint(mouse):
                        if i == 4:
                            grid = reset_grid(screen, squares, grid_size)
                            start_cell, start_xy = None, None
                            end_cell, end_xy = None, None

                        print(f"edit_mode = {str(i)}")
                        edit_mode = i

                        if i == 5: 
                            if start_cell and end_cell:
                                dijkstra(screen, grid, start_xy, end_xy, squares)
                            else:
                                print("ERROR: start/end missing")
                
                if 140 < mouse[0] < 535 and 605 < mouse[1] < 620:
                    print(f"edit_mode = -1")
                    edit_mode = -1

                # choose cell
                for i, r in enumerate(squares):
                    for j, s in enumerate(r):
                        if s.collidepoint(mouse):
                            print(f"collides [{str(edit_mode)}]")
                            if edit_mode not in [-1, 4]:
                                grid = mark_cell(screen, s, grid, (i, j), edit_mode)

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    # TODO add cli flags with getopts (for choosing algo)
    main()
