#!/usr/bin/env python3
import pygame
import sys
import random
from tkinter import Tk, messagebox
from constants import Colours
from algorithms import Dijkstra, AStar


class MessageBox:

    def __init__(self):
        self.window = Tk()
        self.window.wm_withdraw()

    def show_error(self, msg):
        messagebox.showerror("Error", msg)

    def show_info(self, msg):
        messagebox.showinfo("Done", msg)

    def update_and_destroy(self):
        self.window.update()
        self.window.destroy()


class Visual:

    def __init__(self, font):
        self.mark_mode_colours = {
            0: Colours.BLUE.value,
            1: Colours.PURPLE.value,
            2: Colours.BLACK.value,
            3: Colours.WHITE.value
        }
        self.window_size = 900
        self.screen = pygame.display.set_mode([self.window_size + 1, self.window_size + 30])
        self.screen.fill(Colours.PURE_BLACK.value)
        self.algo_selection = 0
        self.edit_mode = -1
        self.grid_size = 60
        self.algo_names = ["Dijkstra", "A*"]
        self.font = font
        self.start_cell = self.end_cell = None
        self.start_xy = self.end_xy = None
        self.edited_squares = []
        self.squares = []
        self.buttons = []

        def setup_grid():
            margin = 1
            margin_removed = self.window_size - self.grid_size * margin
            square_size = round(margin_removed / self.grid_size)

            for r in range(self.grid_size):
                sublist = []
                for c in range(self.grid_size):
                    x = margin + c * (margin + square_size)
                    y = margin + r * (margin + square_size)
                    rect = pygame.Rect(x, y, square_size, square_size)
                    pygame.draw.rect(self.screen, Colours.WHITE.value, rect)
                    sublist.append(rect)

                self.squares.append(sublist)

            self.grid = [[1 for i in range(self.grid_size)] for ii in range(self.grid_size)]

        def setup_buttons_and_labels():
            start_label = self.font.render("Set Start", 1, Colours.WHITE.value)
            end_label = self.font.render("Set End", 1, Colours.WHITE.value)
            obs_label = self.font.render("Set Obs.", 1, Colours.WHITE.value)
            random_label = self.font.render("Randomize", 1, Colours.WHITE.value)
            clear_label = self.font.render("Clear (1)", 1, Colours.WHITE.value)
            clean_label = self.font.render("Clean", 1, Colours.WHITE.value)
            reset_label = self.font.render("Reset", 1, Colours.WHITE.value)
            switch_label = self.font.render("Switch", 1, Colours.WHITE.value)
            findpath_label = self.font.render("Find Path", 1, Colours.WHITE.value)

            labels = [start_label, end_label, obs_label, random_label, clear_label, clean_label, reset_label, switch_label, findpath_label]
            # edit_modes:   0         1          2             3            4            5            6             7               8

            button_margin = 3
            text_width_margin = 4
            text_height_margin = 2
            next_pos = (2, 905)

            for l in labels:
                l_w, l_h = l.get_size()
                bg_w, bg_h = l_w + 2 * text_width_margin, l_h + 2 * text_height_margin
                bg_button = pygame.Rect(next_pos[0], next_pos[1], bg_w, bg_h)
                pygame.draw.rect(self.screen, Colours.WHITE.value, bg_button, 1)
                self.buttons.append(bg_button)

                l_rect = l.get_rect(center=(next_pos[0] + bg_w // 2, next_pos[1] + bg_h // 2))
                self.screen.blit(l, l_rect)

                next_pos = (next_pos[0] + l_w + 2 * text_width_margin + button_margin, next_pos[1])

            algorithm_text_label = self.font.render("Algorithm: ", 1, Colours.WHITE.value)
            algorithm_text_label_size = algorithm_text_label.get_size()
            self.screen.blit(algorithm_text_label, (next_pos[0] + 8, next_pos[1] + 1))

            self.algo_label_start_pos = (next_pos[0] + 8 + algorithm_text_label_size[0], next_pos[1] + 1)
            algorithm_info_label = self.font.render(self.algo_names[self.algo_selection], 1, Colours.WHITE.value)
            self.screen.blit(algorithm_info_label, self.algo_label_start_pos)

        setup_grid()
        setup_buttons_and_labels()

    def check_button_highlight(self, mouse):
        for b in self.buttons:
            if b.collidepoint(mouse):
                pygame.draw.rect(self.screen, Colours.GRAY.value, b.copy(), 1)
            else:
                pygame.draw.rect(self.screen, Colours.WHITE.value, b.copy(), 1)

    def check_paint_obstacle(self, mouse):
        if self.edit_mode == 2:
            for y, r in enumerate(self.squares):
                for x, s in enumerate(r):
                    if s.collidepoint(mouse):
                        pygame.draw.rect(self.screen, Colours.BLACK.value, s)
                        self.grid[y][x] = sys.maxsize

    def check_button_actions(self, mouse):

        def clean_grid():
            for s in self.edited_squares:
                pygame.draw.rect(self.screen, Colours.WHITE.value, s)

            self.edited_squares = []

        def reset_grid():
            for r in self.squares:
                for s in r:
                    pygame.draw.rect(self.screen, Colours.WHITE.value, s)

            self.grid = [[1 for i in range(self.grid_size)] for ii in range(self.grid_size)]
            self.start_cell = self.end_cell = None
            self.start_xy = self.end_xy = None

        def randomize_grid():
            reset_grid()

            for y, r in enumerate(self.squares):
                for x, s in enumerate(r):
                    if random.getrandbits(1):
                        pygame.draw.rect(self.screen, Colours.BLACK.value, s)
                        self.grid[y][x] = sys.maxsize

        def switch_algo():
            clean_grid()

            if self.algo_selection == len(self.algo_names) - 1:
                self.algo_selection = 0
            else:
                self.algo_selection += 1

            self.screen.fill(Colours.PURE_BLACK.value, (self.algo_label_start_pos[0], self.algo_label_start_pos[1], 100, 30))
            name = self.algo_names[self.algo_selection]
            label = self.font.render(name, 1, Colours.WHITE.value)
            self.screen.blit(label, self.algo_label_start_pos)

        def run_algo():
            msgbox = MessageBox()

            if self.start_cell and self.end_cell:
                if self.algo_selection == 0:
                    dijkstra = Dijkstra(self.screen, self.start_xy, self.end_xy, self.squares, self.grid, self.edited_squares)
                    result, self.edited_squares = dijkstra.find_path()
                elif self.algo_selection == 1:
                    a_star = AStar(self.screen, self.start_xy, self.end_xy, self.squares, self.grid, self.edited_squares)
                    result, self.edited_squares = a_star.find_path()

                if result:
                    msgbox.show_info(f"Distance: {str(result)}")
                else:
                    msgbox.show_error("No possible path.")
            else:
                msgbox.show_error("Start or end not set.")

            msgbox.update_and_destroy()

        for i, b in enumerate(self.buttons):
            if b.collidepoint(mouse):
                if i == 3:
                    randomize_grid()
                elif i == 5:
                    clean_grid()
                elif i == 6:
                    reset_grid()
                elif i == 7:
                    switch_algo()
                elif i == 8:
                    run_algo()
                self.edit_mode = i

    def check_cell_actions(self, mouse):

        def set_start_cell():
            if self.start_cell:
                pygame.draw.rect(self.screen, Colours.WHITE.value, self.start_cell)

            pygame.draw.rect(self.screen, self.mark_mode_colours[self.edit_mode], s)
            self.start_cell = s
            self.start_xy = (i, j)

            if self.grid[i][j] == sys.maxsize:
                self.grid[i][j] = 1

        def set_end_cell():
            if self.end_cell:
                pygame.draw.rect(self.screen, Colours.WHITE.value, self.end_cell)

            pygame.draw.rect(self.screen, self.mark_mode_colours[self.edit_mode], s)
            self.end_cell = s
            self.end_xy = (i, j)

            if self.grid[i][j] == sys.maxsize:
                self.grid[i][j] = 1

        def clear_cell():
            pygame.draw.rect(self.screen, Colours.WHITE.value, s)

            if s == self.start_cell:
                self.start_cell = self.start_xy = None
            elif s == self.end_cell:
                self.end_cell = self.end_xy = None
            elif self.grid[i][j] == sys.maxsize:
                self.grid[i][j] = 1

        for i, r in enumerate(self.squares):
            for j, s in enumerate(r):
                if s.collidepoint(mouse) and self.edit_mode in [0, 1, 4]:
                    if self.edit_mode == 0:
                        set_start_cell()
                    elif self.edit_mode == 1:
                        set_end_cell()
                    elif self.edit_mode == 4:
                        clear_cell()
