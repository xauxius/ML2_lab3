from game.gamerules import Board
from classes.state import State
import numpy as np

def play_game(p1, p2, plot_each_move=False):
    board = Board()
    boardStates = []
    turn = 1

    while len(board.getPossibleActions()) > 0:
        for p in [p1, p2]:
            action = p.getAction(board, turn)
            if action not in board.getPossibleActions():
                print("Ilegal move encountered, exiting...")
                return
            
            board.updateBoard(action, turn)

            if plot_each_move:
                board.plotBoard(p1, p2)

            boardStates.append(State.hashBoard(board.board))
            gameWon = board.checkVictory(action, turn)
            if gameWon:
                return (turn, boardStates)
            turn *= -1
    return (0, boardStates)

def test_games(p1, p2, game_count):
    p1_wins = 0
    p1_as_first = 0
    p1_as_second = 0
    p2_wins = 0
    p2_as_first = 0
    p2_as_second = 0
    draws = 0

    for i in range(int(game_count / 2)):
        won1, _ = play_game(p1, p2)
        won2, _ = play_game(p2, p1)

        if won1 == 1:
            p1_wins += 1
            p1_as_first += 1
        elif won1 == -1:
            p2_wins += 1
            p2_as_second += 1
        else:
            draws += 1

        if won2 == 1:
            p2_wins += 1
            p2_as_first += 1
        elif won2 == -1:
            p1_wins += 1
            p1_as_second += 1
        else:
            draws += 1
        print(f"game pair {i}, result: ({won1}; {won2})")

    print(f"p1_wins: {p1_wins}: ({p1_as_first}; {p1_as_second})")
    print(f"p2_wins: {p2_wins}: ({p2_as_first}; {p2_as_second})")
    print(f"draws: {draws}")

def encode_state(state):
    ones = state == 1
    zeros = state == 0
    neg = state == -1
    return np.stack([ones, zeros, neg], axis=2)