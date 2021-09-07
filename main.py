from tkinter import *

import random
import sys
import numpy as np
import pygame
import math

# Final variables
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4


def create_board():
    board_zero = np.zeros((ROW_COUNT, COLUMN_COUNT))  # Create board full in 0's with numpy
    return board_zero


# Change zero to 1\2 (player\AI)
def drop_piece(board, row, col, piece):  # piece = 1/2
    board[row][col] = piece


# Check if the location is empty
def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0  # Check if empty


def get_next_open_row(board, col):
    for row in range(ROW_COUNT):
        if board[row][col] == 0:
            return row


def print_board(board):  # In terminal
    print(np.flip(board, 0))


def winning_move(board, piece):  # Check win
    # Check horizontal locations
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece \
                    and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check vertical locations
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece \
                    and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check main diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece \
                    and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # Check secondary diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece \
                    and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_position(board, piece):  # piece: 1-player, 2-AI
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score main diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score secondary diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_final_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizing_player):
    valid_location = get_valid_locations(board)
    is_final = is_final_node(board)
    if depth == 0 or is_final:
        if is_final:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -100000000000000)
            else:  # Game over - no more valid moves
                return (None, 0)
        else:  # Depth is 0
            return (None, score_position(board, AI_PIECE))

    if maximizing_player:
        value = -math.inf
        best_column = random.choice(valid_location)
        for col in valid_location:
            row = get_next_open_row(board, col)
            board_copy = board.copy()
            drop_piece(board_copy, row, col, AI_PIECE)
            new_score = minimax(board_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_column, value

    else:  # MinimizingPlayer
        value = math.inf
        best_column = random.choice(valid_location)
        for col in valid_location:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if (is_valid_location(board, col)):
            valid_locations.append(col)
    return valid_locations


# ___before minimax___
# def pick_best_move(board, piece):
#     best_score = -10000000
#     valid_location = get_valid_locations(board)
#     best_col = random.choice(valid_location)
#
#     for col in valid_location:
#         row = get_next_open_row(board, col)
#         temp_board = board.copy()
#         drop_piece(temp_board, row, col, piece)
#         score = score_position(temp_board, piece)
#
#         if score > best_score:
#             best_score = score
#             best_col = col
#
#     return best_col


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(screen, BLACK,
                               (int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                                int(r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED,
                                   (int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                                    height - int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW,
                                   (int(c * SQUARE_SIZE + SQUARE_SIZE / 2),
                                    height - int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
    pygame.display.update()


# End of functions

# TK
def start_frame():
    window = Tk()
    window.geometry(str(width) + "x" + str(height))
    # window.eval('tk::PlaceWindow . center')
    window.title("Connect four")

    logo = PhotoImage(file="connect-four.png")
    window.iconphoto(False, logo)

    button1 = Button(window, text="Level 1", font=("Ink free", 30), fg="white", bg="black",
                     command=lambda: choose_level(1, button1, button2, button3))
    button2 = Button(window, text="Level 2", font=("Ink free", 30), fg="white", bg="black",
                     command=lambda: choose_level(2, button1, button2, button3))
    button3 = Button(window, text="Level 3", font=("Ink free", 30), fg="white", bg="black",
                     command=lambda: choose_level(3, button1, button2, button3))

    start_button = Button(window, text="Start", font=("Ink free", 30), fg="white", bg="black",
                          command=lambda: {window.destroy() if flag_button else None})

    button1.pack()
    button2.pack()
    button3.pack()
    start_button.pack()

    window.mainloop()


def choose_level(level_button, button1, button2, button3):
    global flag_button
    flag_button = True
    global level
    print("level ", level_button)
    level = level_button
    if level == 1:
        button1.config(bg="blue")
        button2.config(bg="black")
        button3.config(bg="black")
    elif level == 2:
        button1.config(bg="black")
        button2.config(bg="blue")
        button3.config(bg="black")
    else:
        button1.config(bg="black")
        button2.config(bg="black")
        button3.config(bg="blue")


# Program's start

board = create_board()
print_board(board)
game_over = False

# Start of pygame
pygame.init()

SQUARE_SIZE = 90

width = COLUMN_COUNT * SQUARE_SIZE
height = (ROW_COUNT + 1) * SQUARE_SIZE

size = (width, height)  # Tuple

RADIUS = int(SQUARE_SIZE / 2 - 5)

# Start frame
global flag_button

global level

start_frame()

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect four")
logo = pygame.image.load("connect-four.png")
pygame.display.set_icon(logo)
draw_board(board)
pygame.display.update()

myFont = pygame.font.SysFont("Ink free", 60)

turn = random.randint(PLAYER, AI)  # Who will play first? random

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARE_SIZE / 2)), RADIUS)
            # else:
            #    pygame.draw.circle(screen, YELLOW, (posx, int(SQUARE_SIZE / 2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
            # Ask for player 1 Input
            if turn == PLAYER:
                posx = event.pos[0]  # Get Position x of the mouse click
                col = int(math.floor(posx / SQUARE_SIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myFont.render("Player 1 Wins!", True, RED)
                        screen.blit(label, (150, 15))
                        print("Player 1 wins!")
                        game_over = True

                    turn += 1
                    turn = turn % 2  # just zero or one

                    print_board(board)
                    draw_board(board)

    # Ask for player 2 Input
    if turn == AI and not game_over:

        # col = random.randint(0,  COLUMN_COUNT-1)  # Easy = Ramdom
        # col = pick_best_move(board, AI_PIECE)
        # col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)
        if level == 1:
            col = random.randint(0, COLUMN_COUNT - 1)  # Easy = Ramdom
        elif level == 2:
            col, minimax_score = minimax(board, 2, -math.inf, math.inf, True)
        else:
            col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            # pygame.time.wait(500)  # Delay of half second
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                print("Player 2 wins!")
                label = myFont.render("Player 2 Wins!", True, YELLOW)
                screen.blit(label, (150, 15))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2  # just zero or one

    if game_over:
        pygame.time.wait(3000)
