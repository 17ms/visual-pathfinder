#!/usr/bin/env python3
import pygame
from pygame.locals import *
from visual import Visual


def main():
    pygame.init()
    pygame.display.set_caption("visual-pathfinder")
    clock = pygame.time.Clock()

    visual = Visual(pygame.font.SysFont("Ubuntu", 15))

    done = 0
    while not done:
        mouse = pygame.mouse.get_pos()

        # having paint_obstacle check inside default event loop prevents "continuous painting"
        if pygame.mouse.get_pressed()[0]:
            visual.check_paint_obstacle(mouse)

        visual.check_button_highlight(mouse)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                done = 1
            elif e.type == pygame.MOUSEBUTTONDOWN:
                visual.check_button_actions(mouse)
                visual.check_cell_actions(mouse)

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()
