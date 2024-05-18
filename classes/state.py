class State:
    n = 6
    m = 7
    def __init__(self, board):
        self.hash_val = State.hashBoard(board)

    @classmethod
    def hashBoard(cls, board):
        hashed = ""
        for i in range(State.n):
            for j in range(State.m):
                hashed += str(int(board[i, j]) + 1)
        return hashed
    
    @classmethod
    def unhashBoard(cls, hashed):
        board = np.zeros((State.n, State.m))
        for i in range(State.n):
            for j in range(State.m):
                ind = i * State.m + j 
                board[i, j] = int(hashed[ind]) - 1
        return board