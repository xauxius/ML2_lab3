#!/usr/bin/env python

import zipfile, glob, os, shutil

from random import shuffle


import numpy as np

import pprint


import gamesrules

from pprint import pprint


DATA_LIMIT = 20.1 * 1024 * 1024 # total data limit + zip "overhead"
IGNORE_FILES=["matchmaking.py","gamesrules.py"]

SECURE_MODE = False # if True, run from docker (windows is not supported)


def uncompressed_underlimit(zipfile):
  total_size = 0
  total_count = 0
  for z in zipfile.filelist:
    total_count = 0
    if (z.is_dir()):
      continue
    with zipfile.open(z) as f:
      while (l := f.read(DATA_LIMIT)):
        total_size = total_size + len(l)
        if (total_size > DATA_LIMIT):
          return False

  if total_count > 2000: # too much files
    return False
  return True;
  pass


def search_entrypoint(zipfile):
  """ return True, entrypoint or False, message"""
  lst = zipfile.filelist
  first_dir_files = list(filter(lambda x : x.filename.count("/") == 1 and x.is_dir() == False,lst))
  root_dir_files = list(filter(lambda x : x.filename.count("/") == 0 and x.is_dir() == False,lst))
  
  to_consider = root_dir_files
  
  
  if len(root_dir_files) == 0:
    to_consider = first_dir_files

  to_consider = list(filter(lambda x : x.filename.split("/")[-1] not in IGNORE_FILES,to_consider))


  if len(to_consider) == 0:
      return False, "no entry point found";

  if len(to_consider) == 1:
      return True, to_consider[0].filename

  if len(to_consider) > 1:
    for j in to_consider:
      if j.filename.endswith("main.py"):
        return True,j.filename
    return False,"no main.py found"
     

def collect_players(workdir="testai"):
  """ return tuple with with zip archives and main py files
  """

  players = []

  g = glob.glob(f"{workdir}/*.zip")
  for i in g:
    if os.stat(i).st_size > DATA_LIMIT:
      print(f"ignoring `{i}' because too big, submitted size is {DATA_LIMIT/1024/1024:.2f} Mb")
      continue
    with zipfile.ZipFile(i) as z:
      if not uncompressed_underlimit(z):
        print(f"ignoring `{i}' because uncompressed data too big")
        continue

      found, ep_name_error = search_entrypoint(z)
      if not found:
        print(f"ignoring `{i}' due entry point failure: {ep_name_error}")

    players.append((i,ep_name_error,os.path.basename(i)))

  return players



def extract_data(players,workdir="tmp"):
  if os.path.exists(workdir):
    shutil.rmtree(workdir)
  os.mkdir(workdir)

  for i in players:
    with zipfile.ZipFile(i[0]) as z:
      bn = os.path.basename(i[0])
      z.extractall(f"{workdir}/{bn}")


# docker pull condaforge/mambaforge
# cd matchmaking-docker
# docker build -t game-image .


# collect all players
players = collect_players();
pnum = len(players)
scores_table = np.zeros((pnum))

np_names = { idx : i[0] for idx,i in enumerate(players)}


print("collected %d players" % (pnum,))

print(players)
extract_data(players)


print(np_names)

rounds = []
for a in range(pnum):
  for b in range(a,pnum):
    if a == b : continue
    z = [a,b]
    shuffle(z) # shuffle starts
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

crash_on_start = 10 # crash on start 10 points



#print(players)
for idx, i in enumerate(rounds):
  scores = [0,0,0]
  #print("Playing %s vs %s " % (np_names[i[0]],np_names[i[1]]))
  p1i = players[i[0]]
  p2i = players[i[1]]

  if p1i != old_p1i:
    if p1:
      p1.kill_process()
      del p1

    p1 = gamesrules.RemotePlayerServer(f"tmp/{p1i[2]}/{p1i[1]}")
    old_p1i = p1i

  if p2i != old_p2i:
    if p2:
      p2.kill_process()
      del p2

    p2 = gamesrules.RemotePlayerServer(f"tmp/{p2i[2]}/{p2i[1]}")
    old_p2i = p2i

  try:
    p1.ping(10)
    p1.newGame(True);

  except:
    print(f"{p1i[0]} crashed on startup - ignoring round")

  try:
    p2.ping(10)
    p2.newGame(True);

  except:
    print(f"{p2i[0]} crashed on startup - ignoring round")



  for j in range(rounds1):
    board = gamesrules.Board()
    
    name1 = p1.getName()
    name2 = p2.getName()

    np_names[ i[0] ] = name1
    np_names[ i[1] ] = name2
    
    p1.newGame(False)
    p1.newGame(False)
    
    r = board.sampleGame(p1,p2);
    
    if r == 0:
     scores[2]+=1
    elif r== -1:
      scores[0]+=1
    elif r== 1 :
      scores[1]+=1
    
    pass

  for j in range(rounds2):
    board = gamesrules.Board()
    
    p1.newGame(False)
    p2.newGame(False)
    
    r = board.sampleGame(p2,p1);
    
    if r == 0:
     scores[2]+=1
    elif r== -1:
      scores[1]+=1
    elif r== 1 :
      scores[0]+=1
    
    pass
  
  scores_table[i[0]] = scores[0] * 2 + scores[2]
  scores_table[i[1]] = scores[1] * 2 + scores[2]
  

al = []

for i in range(pnum):
  al.append((scores_table[i],np_names[i]))

print("*********************************score table*********\n")
al = sorted(al,key=lambda x: x[0],reverse=True)
print("place, score, name")
for idx,i in enumerate(al):
  print("%2d: %3.0f %s" % (idx+1,i[0],i[1]))
