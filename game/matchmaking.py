#!/usr/bin/env python

from random import shuffle

import numpy as np
import gamerules
import utils


utils.DATA_LIMIT = 20.1 * 1024 * 1024  # total data limit + zip "overhead"
utils.IGNORE_FILES = ["matchmaking.py", "gamerules.py", "gamesrules.py"]

SECURE_MODE = True  # if True, run from docker (windows is not supported) in safe envirioment


def check_or_restart(p):
    """ check or restart client if necessary """
    try:
        p.ping(5)  # any exception -> client crashed
    except:
        p.check_for_restart()
        p.ping(10)
        p.newGame(True)


# docker pull condaforge/mambaforge
# cd matchmaking-docker
# docker build -t game-image .


# collect all players
players = utils.collect_players()
pnum = len(players)
scores_table = np.zeros((pnum))

np_names = {idx: i[0] for idx, i in enumerate(players)}


print("collected %d players" % (pnum,))

print(players)
utils.extract_data(players)


print(np_names)

rounds = []
for a in range(pnum):
    for b in range(a, pnum):
        if a == b:
            continue
        z = [a, b]
        shuffle(z)  # shuffle starts
        rounds.append(z)


# shuffle list
shuffle(rounds)

print("Perform game")

old_p1i = None
old_p2i = None

p1 = None
p2 = None

rounds1 = 5
rounds2 = 5

# print(players)
for idx, i in enumerate(rounds):
    scores = [0, 0, 0]
    #print("Playing %s vs %s " % (np_names[i[0]],np_names[i[1]]))
    p1i = players[i[0]]
    p2i = players[i[1]]

    can_play = True

    if p1i != old_p1i:
        if p1:
            p1.kill_process()
            del p1

        p1 = gamerules.RemotePlayerServer(f"tmp/{p1i[2]}/{p1i[1]}", secure_mode=SECURE_MODE)
        old_p1i = p1i

    if p2i != old_p2i:
        if p2:
            p2.kill_process()
            del p2

        p2 = gamerules.RemotePlayerServer(f"tmp/{p2i[2]}/{p2i[1]}", secure_mode=SECURE_MODE)
        old_p2i = p2i

    try:
        p1.ping(10)
        p1.newGame(True)

    except:
        print(f"{p1i[0]} crashed on startup - ignoring round")
        can_play = False

    try:
        p2.ping(10)
        p2.newGame(True)

    except:
        print(f"{p2i[0]} crashed on startup - ignoring round")
        can_play = False
        p2.kill_process()
        old_p2i = None

    if not can_play:
        continue

    for j in range(rounds1):
        board = gamerules.Board()

        name1 = p1.getName()
        name2 = p2.getName()

        np_names[i[0]] = name1
        np_names[i[1]] = name2

        p1.newGame(False)
        p1.newGame(False)

        r = board.sampleGame(p1, p2)

        check_or_restart(p1)
        check_or_restart(p2)

        # calculate score
        if r == 0:
            scores[2] += 1
        elif r == -1:
            scores[0] += 1
        elif r == 1:
            scores[1] += 1

        pass

    for j in range(rounds2):
        board = gamerules.Board()

        p1.newGame(False)
        p2.newGame(False)

        r = board.sampleGame(p2, p1)

        check_or_restart(p1)
        check_or_restart(p2)

        if r == 0:
            scores[2] += 1
        elif r == -1:
            scores[1] += 1
        elif r == 1:
            scores[0] += 1

        pass

    scores_table[i[0]] = scores[0] * 2 + scores[2]
    scores_table[i[1]] = scores[1] * 2 + scores[2]


al = []

for i in range(pnum):
    al.append((scores_table[i], np_names[i]))

print("*********************************score table*********************************\n")
al = sorted(al, key=lambda x: x[0], reverse=True)
print("place, score, name")
for idx, i in enumerate(al):
    print("%2d: %3.0f %s" % (idx+1, i[0], i[1]))
