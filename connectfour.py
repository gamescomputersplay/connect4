####################
# Connect Four Bot #
####################

# by GamesComputersPlay
# https://www.youtube.com/watch?v=IpTFe0H52JM


# Some settings
###############

# Default depth of the minimax algorithm
# Larger number produces stronger play,
# but exponentially increases required time
setDefaultDepth = 6

# Some values for the heuristic part of the program
# Chosen pretty arbitrary, TBH
setScoreFor2 = 1  # Point for 2 discs
setScoreFor3 = 5  # Point for 3 discs
setNegWeight = 1.5  # How much less oppoment's score weights


# Class for one game position
class Connect4Board:

    # Create instance
    # Initialize board (empty if none)
    # Board is a string of 42 characters, " ", "X" or "0",
    # showing cells line by line top to bottom
    # initialize last move variable to -1 (no last move)
    def __init__(self, initBoard=" "*42):
        self.board = initBoard
        self.lastMove = -1

    # Nice string representation of a board for printing
    def __str__(self):
        buffer = "|"
        for i in range(len(self.board)):
            buffer += self.board[i]
            if (i + 1) % 7 == 0 and i != len(self.board) - 1:
                buffer += "|\n|"
        buffer += "|"
        return buffer

    # How many plies has been made so far
    def pliesMade(self):
        return 42-self.board.count(" ")

    # Functions related to playing the game
    #########################################

    # Play a disc in column col (0-based)
    # player: 1 for player "X"; -1 for player "0"
    # (!) Does not check if the column is playable, use legitMoves for that
    # returns winner ("X" or "0") if the move results in someone's victory
    # returns "" if there is no winner
    # Also, sets lastMove variable
    def makeMove(self, player, col):
        mark = "X" if player == 1 else "0"
        for i in range(5, -1, -1):
            if self.board[i * 7 + col] == " ":
                place = i * 7 + col
                self.board = self.board[:place] + mark + self.board[place+1:]
                self.lastMove = place
                return self.winner()

    # Returns a list of all availabe moves (0-based column numbers)
    # Move is available if there are less than 6 discs in that column
    def legitMoves(self):
        legitMoves = []
        # Move exploration order to optimize the performance (+2%)
        for i in [3, 2, 4, 1, 5, 0, 6]:
            if self.board[i] == " ":
                legitMoves.append(i)
        return legitMoves

    # Returns a winner ("X", "0" or ""), but only based on the lastMove
    # (using only last move is for speed optimization in Minimax part)
    def winner(self):
        if self.lastMove == -1:
            return ""
        this = self.board[self.lastMove]
        for line in wSlotsByCells[self.lastMove]:
            if self.board[line[0]] == this and \
               self.board[line[1]] == this and \
               self.board[line[2]] == this:
                return this
        return ""

    # Returns a winner ("X", "0" or ""), based on the whole board
    # This is used in scoring part of the algorithm
    def winner_brute(self):
        for line in wSlots:
            if self.board[line[0]] != " " and\
               self.board[line[0]] == self.board[line[3]] and \
               self.board[line[0]] == self.board[line[2]] and \
               self.board[line[0]] == self.board[line[1]]:
                return self.board[line[0]]
        return ""

    # Naive part of the algorithm
    #############################

    # Check if any one move of the player "player" can win the game
    # return N of the column or -1 there is no such move
    def instaWin(self, player):
        mark = "X" if player == 1 else "0"
        for col in self.legitMoves():
            newBoard = Connect4Board(self.board)
            isWin = newBoard.makeMove(player, col)
            if isWin != "":
                return col
        return -1

    # Minimax mart of the algorythm
    ################################

    # Base of the minimax
    # returns the list of outcomes:
    #   N of winning player (1/-1) or 0 for indeterminate/draw
    # player: which player we are gettign the reuslts for
    # depth: plies to go through
    def minimax(self, player, depth):
        minimax = []
        for i in range(7):
            if i not in self.legitMoves():
                minimax.append(-999 * player)
                continue
            newState = Connect4Board(self.board)
            newState.makeMove(player, i)
            res = newState.addPly(player * -1, depth - 1)
            minimax.append(res)
        return minimax

    # Recursive part of teh minimax
    # player: player for THIS layer of the tree
    # depth: remaining depth to go through
    def addPly(self, player, depth):
        results = []
        for i in self.legitMoves():
            newState = Connect4Board(self.board)
            winner = newState.makeMove(player, i)
            if winner == "" and depth > 1:
                result = newState.addPly(player * -1, depth - 1)
            else:
                if winner == "":
                    result = 0
                else:
                    result = 1 if winner == "X" else -1
            results.append(result)
            # alpha-beta pruning
            if player == 1 and result > 0:
                return result
            if player == -1 and result < 0:
                return result

        if len(results) == 0:
            return 0
        if player == 1:
            return max(results)
        if player == -1:
            return min(results)

    # Heuristic part of the algorithm
    #################################

    # Returns a "Score" of the board
    # (based on the number of 2's and 3's that can potential to become 4's)
    # Scores values settings are in the beginning of this file
    # player - which player to use to get the scores (1 for "X", -1 for "0")
    def getOneScore(self, player):
        mark = "X" if player == 1 else "0"
        otherMark = "0" if player == 1 else "X"
        score = 0
        for line in wSlots:
            thisLineCount = 0
            for i in range(4):
                if self.board[line[i]] == otherMark:
                    break
                if self.board[line[i]] == mark:
                    thisLineCount += 1
            else:
                if thisLineCount == 2:
                    score += setScoreFor2
                if thisLineCount == 3:
                    score += setScoreFor3
        return score

    # Returns a list of scores for all 7 postential moves
    def getScores(self, player):
        scores = [0, 0, 0, 0, 0, 0, 0]
        for i in self.legitMoves():
            newState = Connect4Board(self.board)
            newState.makeMove(player, i)
            scores[i] = newState.getOneScore(player)
        return scores

    # Using all 3 parts of the algorithm together
    #############################################

    # Choose the best move,
    # by weighing together results of minimax and heuristic algorithms
    # player: player we chose for (1 for "X", -1 for "0")
    # minimax: list of minimax results
    # pScores (positive scores): scoring results for this player
    # nScores (negative scores): scoring results for the opponent
    # verbose: if True, print out some weights data
    def considerAll(self, player, minimax, pScores, nScores, verbose):

        # pick best minimax result
        best = []
        func = max if player == 1 else min
        for i in range(7):
            if minimax[i] == func(minimax):
                best.append(i)
        if verbose:
            print ("Minimax list:", best)
        if len(best) == 1:
            return best[0]

        # if tied, pick best pScore+nScore
        weights = [0, 0, 0, 0, 0, 0, 0]
        for i in best:
            weights[i] = int(pScores[i] + nScores[i] / setNegWeight)
        if verbose:
            print ("Score weights:", weights)

        best2 = []
        for i in best:
            if weights[i] == max(weights):
                best2.append(i)
        if len(best2) == 1:
            return best2[0]

        # if tied, pick the most central one
        centrals = [0, 0, 0, 0, 0, 0, 0]
        for i in best2:
            centrals[i] = 4 - abs(3 - i)
        if verbose:
            print ("Centralness weights:", centrals)
        best3 = []
        for i in best2:
            if centrals[i] == max(centrals):
                best3.append(i)
        if len(best3) == 1:
            return best3[0]

        return best3[self.pliesMade() % len(best3)]

    # Main function of the module:
    # Choose teh best move in this position
    # player: who are we chose the move for (1 for "X", -1 for "0")
    # depth: N of plies to go through for minimax part
    # verbose: if True, print some data about how decision is made
    # returns 0-based column number
    def chooseMove(self, player=1, depth=setDefaultDepth, verbose=False):

        # 1. If there is an InstaWin - go for it
        instawin = self.instaWin(player)
        if instawin != -1:
            if verbose:
                print ("Instawin at", instawin)
            return instawin

        # 2. If an opponent has an instawin - block it
        instalose = self.instaWin(player*-1)
        if instalose != -1:
            if verbose:
                print ("Counter Instawin at", instalose)
            return instalose

        # 3. Minimax
        minimax = self.minimax(player, depth)
        if verbose:
            print ("Minimax:", minimax)

        # 4. Positive score
        pScores = self.getScores(player)
        if verbose:
            print ("Positive score:", pScores)

        # 5. Negative score
        nScores = self.getScores(player*-1)
        if verbose:
            print ("Negative Score:", nScores)

        # Combine 3,4,5, central distance and pseudo-randomness
        bestmove = self.considerAll(player, minimax, pScores, nScores, verbose)

        return bestmove

# end of Connect4Board class


# Some helper functions to facilitate searching for the winner
##############################################################

# Generate and return a list of all possible winning lines
# number are indices in a 42-character line. representing the board
# [ [0, 1, 2, 3], [1, 2, 3, 4],... [37, 31, 25, 19], [38, 32, 26, 20] ]
def genSlots():
    wSlots = []
    # horisontal
    for i in range(6):
        for j in range(4):
            line = []
            for k in range(4):
                line.append(i * 7 + j + k)
            wSlots.append(line)
    # vertical
    for i in range(7):
        for j in range(3):
            line = []
            for k in range(4):
                line.append((i + j * 7 + k * 7))
            wSlots.append(line)
    # diagonal falling
    for i in range(3):
        for j in range(4):
            line = []
            for k in range(4):
                line.append((i * 7 + j + k * 7 + k))
            wSlots.append(line)
    # diagonal rising
    for i in range(3, 6):
        for j in range(4):
            line = []
            for k in range(4):
                line.append((i * 7 + j - k * 7 + k))
            wSlots.append(line)
    return wSlots


# Generate and return a set of lists of winning lines
# from a particular cell (excluding the cell itself)
# Sounds very complicated, so here's the example:
# {0: [[1, 2, 3], [7, 14, 21], [8, 16, 24]], 1: [[0, 2, 3], ...
# It means if you have a disc in position 0, the to form
# a winning line, you have to have discs
# in positions 1-2-3, 7-14-21 or 8-16-24
def genSlotsByCell():
    out = {}
    for i in range(42):
        out[i] = []
        for line in wSlots:
            if i in line:
                line_shorten = line.copy()
                line_shorten.remove(i)
                out[i].append(line_shorten)
    return out

# Initialize helper lists
wSlots = genSlots()
wSlotsByCells = genSlotsByCell()


# end of connectfour module

# If the file is run directly: a brief demo,
# program plays against itself with the defalt parameters

if __name__ == "__main__":

    import time

    g = Connect4Board()
    player = 1

    while len(g.legitMoves()) > 0 and g.winner() == "":

        t = time.time()

        print("=" * 20, g.pliesMade(), "=" * 20)
        move = g.chooseMove(player, verbose=True)
        g.makeMove(player, move)

        print ("Player", "X" if player == 1 else "0", "goes:", move)
        print ("Time spent on this move", time.time() - t)
        print (g)

        player *= -1

    print ("=" * 20, "final position", "=" * 20)
    print (g)
    print (g.winner() if g.winner() != "" else "no one", "won")
