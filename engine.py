"""Tic Tac Toe 3x3: AI là MAX, đối thủ là MIN, tìm đến cuối ván."""
from functools import lru_cache

LINES = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))

def winning_line(board):
    return next((line for line in LINES if board[line[0]] and
                 board[line[0]] == board[line[1]] == board[line[2]]), ())

def result(board):
    line = winning_line(board)
    if line:
        return board[line[0]]
    return 'draw' if all(board) else None

def other(player):
    return 'O' if player == 'X' else 'X'

@lru_cache(maxsize=20000)
def minimax(board, turn, ai):
    outcome = result(board)
    if outcome:
        return 0 if outcome == 'draw' else (1 if outcome == ai else -1)
    values = []
    for i, cell in enumerate(board):
        if not cell:
            child = board[:i] + (turn,) + board[i+1:]
            values.append(minimax(child, other(turn), ai))
    return (max if turn == ai else min)(values)

def best_move(board, ai):
    if result(board):
        return None
    # Ưu tiên giữa, góc khi các nước có cùng giá trị Minimax.
    order = (4,0,2,6,8,1,3,5,7)
    choices = [i for i in order if not board[i]]
    return max(choices, key=lambda i: minimax(
        tuple(board[:i]) + (ai,) + tuple(board[i+1:]), other(ai), ai))
