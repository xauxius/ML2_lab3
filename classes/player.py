import numpy as np
from game.gamerules import Player

class MyPlayer(Player):
    def __init__(self):
        super().__init__("Paulius Černius")

    def getAction(self, board, value):
        """ All logic going here """
        possibleActions = board.getPossibleActions()
        return np.random.choice(possibleActions)

    def newGame(self, new_opponent):
        pass

class RNGPlayer(Player):
    def __init__(self):
        super().__init__("RNG player")

    def getAction(self, board, Value):
        """ All logic going here """
        possibleActions = board.getPossibleActions()
        return np.random.choice(possibleActions)

    def newGame(self, new_opponent):
        pass