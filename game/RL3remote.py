#!/usr/bin/env python
"""
Simple test for sandboxed execution

"""
import gamerules


import numpy as np
import matplotlib.pyplot as plt
import os


p1 = gamerules.RemotePlayerServer("./RL3.py")
p2 = gamerules.RemotePlayerServer("./RL3.py")

board = gamerules.Board()
gameFinished = False


board.sampleGame(p1, p2)
# inform player game is finished
for i in [p1, p2]:
    i.stop_playing()

board.showBoard()
board.plotBoard(p1, p2)
