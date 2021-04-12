import curses as c
import math
import sys
import time
from random import randrange

BLOCK = 9608
BG_COLOR = 16 # 0-15 reserved for terminal palette
MZ_COLOR = 17
PL_COLOR = 18

def exit_game(scr):
    c.nocbreak()
    scr.keypad(False)
    c.echo()
    c.endwin()
    sys.exit(0)


def show_win_banner(scr):
    max_yx = scr.getmaxyx()
    mid_y = math.floor(max_yx[0] / 2)
    mid_x = math.floor(max_yx[1] / 2)
    msg = 'WINNER WINNER CHICKEN DINNER'

    msg_win = scr.subwin(3, len(msg) + 2, mid_y - 1, mid_x - math.floor(len(msg) / 2))
    msg_win.box()
    msg_win.addstr(1, 1, msg)
    scr.refresh()
    msg_win.refresh()

    key = None 
    while key != 'q':
        key = msg_win.getkey()
    exit_game(scr)


def play_maze(scr, maze):
    max_y = len(maze) - 1
    max_x = len(maze[0]) - 1
    pos_x = 0
    pos_y = 0
    #pos_x = max_x     #For debug
    #pos_y = max_y - 1

    while(not (pos_x is max_x and pos_y is max_y)):
        color_path(pos_x, pos_y, scr, c.color_pair(PL_COLOR))
        key = scr.getkey()
        if (key == 'k' or key == 'KEY_UP') and (pos_y - 1 >= 0 and maze[pos_y - 1][pos_x] == 1):
            color_path(pos_x, pos_y - 1, scr, c.color_pair(PL_COLOR))
            color_path(pos_x, pos_y, scr, c.color_pair(MZ_COLOR))
            pos_y -= 1
        elif (key == 'j' or key == 'KEY_DOWN') and (pos_y + 1 <= max_y and maze[pos_y + 1][pos_x] == 1):
            color_path(pos_x, pos_y + 1, scr, c.color_pair(PL_COLOR))
            color_path(pos_x, pos_y, scr, c.color_pair(MZ_COLOR))
            pos_y += 1
        elif (key == 'h' or key == 'KEY_LEFT') and (pos_x - 1 >= 0 and maze[pos_y][pos_x - 1] == 1):
            color_path(pos_x - 1, pos_y, scr, c.color_pair(PL_COLOR))
            color_path(pos_x, pos_y, scr, c.color_pair(MZ_COLOR))
            pos_x -= 1
        elif (key == 'l' or key == 'KEY_RIGHT') and (pos_x + 1 <= max_x and maze[pos_y][pos_x + 1] == 1):
            color_path(pos_x + 1, pos_y, scr, c.color_pair(PL_COLOR))
            color_path(pos_x, pos_y, scr, c.color_pair(MZ_COLOR))
            pos_x += 1
        elif (key == 'q'):
            exit_game(scr)

    show_win_banner(scr)


def color_path(x, y, scr, color):
    scr.addch(y, x, chr(BLOCK), color)
    scr.refresh()
    time.sleep(0.005)


def visit_neighbor(cell, neighbor, maze, scr):
    cell_y = cell[0] + 2 # Offset for starting path
    cell_x = cell[1]
    neighbor_y = neighbor[0] + 2
    neighbor_x = neighbor[1]

    if cell_y != neighbor_y:
        if cell_y < neighbor_y:
            maze[cell[0] + 1][cell_x] = 1
            for i in range(1, 3):
                color_path(cell_x, cell_y + i, scr, c.color_pair(MZ_COLOR))
        else:
            maze[cell[0] - 1][cell_x] = 1
            for i in range(1, 3):
                color_path(cell_x, cell_y - i, scr, c.color_pair(MZ_COLOR))
    else:
        if cell_x < neighbor_x:
            maze[cell[0]][cell_x + 1] = 1
            for i in range(1, 3):
                color_path(cell_x + i, cell_y, scr, c.color_pair(MZ_COLOR))
        else:
            maze[cell[0]][cell_x - 1] = 1
            for i in range(1, 3):
                color_path(cell_x - i, cell_y, scr, c.color_pair(MZ_COLOR))


def get_unvisited_neighbors(maze, cell, x_lim, y_lim):
    y = cell[0]
    x = cell[1]
    unvisited = []

    if y - 2 >= 0 and maze[y - 2][x] == 0: unvisited.append((y - 2, x))     # north
    if y + 2 <= y_lim and maze[y + 2][x] == 0: unvisited.append((y + 2, x)) # south
    if x - 2 >= 0 and maze[y][x - 2] == 0: unvisited.append((y, x - 2))     # east
    if x + 2 <= x_lim and maze[y][x + 2] == 0: unvisited.append((y, x + 2)) # west
    
    return unvisited


def generate_maze(scr, maze, start_x, start_y):
    stack = []
    x_lim = len(maze[0]) - 1
    y_lim = len(maze) - 1

    maze[start_y][start_x] = 1
    color_path(start_x, start_y + 2, scr, c.color_pair(MZ_COLOR))
    stack.append((start_y, start_x))

    while(stack):
        cell = stack.pop()
        unvisited = get_unvisited_neighbors(maze, cell, x_lim, y_lim)
        if unvisited:
            stack.append(cell)
            neighbor = unvisited[randrange(0, len(unvisited))]
            visit_neighbor(cell, neighbor, maze, scr)
            maze[neighbor[0]][neighbor[1]] = 1
            stack.append(neighbor)


def main(stdscr):
    c.curs_set(0)
    c.use_default_colors()
    c.init_pair(BG_COLOR, c.COLOR_BLACK, -1)
    c.init_pair(MZ_COLOR, c.COLOR_WHITE, -1)
    c.init_pair(PL_COLOR, c.COLOR_RED, -1)

    maze_cols = c.COLS - 1
    maze_lines = c.LINES
    if (c.COLS - 1) % 2 != 1:
        maze_cols = c.COLS - 2

    if c.LINES % 2 != 1:
        maze_lines = c.LINES - 1

    maze = [[0 for x in range(0, maze_cols)] for y in range(0, maze_lines)]
    for i in range(0, 2): maze[i][0] = 1
    for i in range(maze_lines - 2, maze_lines): maze[i][-1] = 1

    for y in range(0, maze_lines):
        for x in range(0, maze_cols):
            stdscr.addch(y, x, chr(BLOCK), c.color_pair(BG_COLOR))
            stdscr.refresh()

    for i in range(0, 2): color_path(0, i, stdscr, c.color_pair(MZ_COLOR))
    for i in range(maze_lines - 2, maze_lines): color_path(maze_cols - 1, i, stdscr, c.color_pair(MZ_COLOR))
    generate_maze(stdscr, maze[2 : maze_lines - 1], 2, 0)
    play_maze(stdscr, maze)


c.wrapper(main)
