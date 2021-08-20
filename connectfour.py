# Connect Four Module

# see at the end of the file for usage example

#settings
setDefaultDepth=6
setScoreFor2=1
setScoreFor3=5
setNegWeight=1.5


# GameState class
class ConfState:

    # set board (empty if none)
    # initialize last move var
    def __init__(self, initBoard=" "*42):
        self.board = initBoard
        self.lastMove=-1

    # Nice print of a board
    def __str__(self):
        buffer = "|"
        for i in range(len(self.board)):
            buffer += self.board[i]
            if (i+1)%7==0 and i!=len(self.board)-1:
                buffer += "|\n|"
        buffer += "|"
        return buffer

    #Add a mark to a board, in column col
    # player 1=X; -1=0
    def makeMove(self,player,col):
        mark = "X" if player==1 else "0"
        for i in range(5,-1,-1):
            if self.board[i*7+col]==" ":
                place = i*7+col
                self.board = self.board[:place] + mark + self.board[place+1:]
                self.lastMove=place
                return self.winner()
                
            
    # return a list of availabe moves (col numbers)
    def legitMoves(self):
        legitMoves=[]
        for i in range(7):
            if self.board[i]==" ":
                legitMoves.append(i)
        return legitMoves
    
    # Check for a winner on a board
    # uses last move data for speed optimization
    def winner(self):
        if self.lastMove==-1:
            return ""
        this = self.board[self.lastMove]
        for line in wSlotsByCells[self.lastMove]:
            if self.board[line[0]]==this and \
               self.board[line[1]]==this and \
               self.board[line[2]]==this:
                return this
        return ""

    def winner_brute(self):
        for line in wSlots:
            if self.board[line[0]]!=" " and\
               self.board[line[0]]==self.board[line[3]] and \
               self.board[line[0]]==self.board[line[2]] and \
               self.board[line[0]]==self.board[line[1]]:
                return self.board[line[0]]
        return ""

    def getOneScore(self,player):
        mark = "X" if player==1 else "0"
        otherMark = "0" if player==1 else "X"
        score = 0
        for line in wSlots:
            thisLineCount=0
            for i in range(4):
                if self.board[line[i]]==otherMark:
                    break
                if self.board[line[i]]==mark:
                    thisLineCount+=1
            else:
                if thisLineCount==2:
                    score+=setScoreFor2
                if thisLineCount==3:
                    score+=setScoreFor3
        return score


    def getScores(self,player):
        scores=[0,0,0,0,0,0,0]   
        for i in self.legitMoves():
            newState = ConfState(self.board)
            newState.makeMove(player,i)
            scores[i]=newState.getOneScore(player)
        return scores
        
    
    # How many plies has been made so far
    def pliesMade(self):
        return 42-self.board.count(" ")

    
    # Check if any one move of the player can win the game
    # return N of the column or -1 there is no such move
    def instaWin(self, player):
        mark = "X" if player==1 else "0"
        for col in self.legitMoves():
            newBoard=ConfState(self.board)
            isWin = newBoard.makeMove(player,col)
            if isWin!="":
                return col
        return -1

    def minimax(self,player,depth):
        minimax=[]   
        for i in range(7):
            if i not in self.legitMoves():
                minimax.append(-999*player)
                continue
            newState = ConfState(self.board)
            newState.makeMove(player,i)
            res = newState.addPly(player*-1, depth-1)
            minimax.append(res)
        return minimax

    def addPly(self, player, depth):
        results = []
        for i in self.legitMoves():
            newState = ConfState(self.board)
            winner = newState.makeMove(player,i)
            if winner=="" and depth>1:
                result = newState.addPly(player*-1, depth-1)
            else:
                if winner=="":
                    result = 0
                else:
                    result = 1 if winner=="X" else -1
            results.append(result)
            # alpha-beta pruning
            if player==1 and result>0:
                return result
            if player==-1 and result<0:
                return result
        
        if len(results)==0:
            return 0
        if player==1:
            return max(results)
        if player==-1:
            return min(results)

    def considerAll(self, player, minimax, pScores, nScores, verbose):

        # pick best minimax result
        best = []
        func = max if player==1 else min
        for i in range(7):
            if minimax[i]==func(minimax):
                best.append(i)
        if verbose: 
            print ("Minimax list:", best)
        if len(best)==1:
            return best[0]

        # if tied, pick best pScore+nScore
        weights = [0,0,0,0,0,0,0]
        for i in best:
            weights[i] = int( pScores[i] + nScores[i]/setNegWeight  )
        if verbose:
            print ("Score weights:", weights)

        best2=[]
        for i in best:
            if weights[i]==max(weights):
                best2.append(i)
        if len(best2)==1:
            return best2[0]

        # if tied, pick the most central one
        centrals = [0,0,0,0,0,0,0]
        for i in best2:
            centrals[i]=4-abs(3-i)
        if verbose:
            print ("Central weights:",centrals)
        best3=[]
        for i in best2:
            if centrals[i]==max(centrals):
                best3.append(i)
        if len(best3)==1:
            return best3[0]

        return best3[self.pliesMade()%len(best3)]
            
    
    # Chose the next move
    def chooseMove(self, player=1, depth=setDefaultDepth, verbose=False):

        # 1. If there is an InstaWin - go for it
        instawin = self.instaWin(player)
        if instawin!=-1:
            if verbose:
                print ("Instawin at", instawin)
            return instawin

        # 2. If an opponent has an instawin - block it
        instalose = self.instaWin(player*-1)
        if instalose!=-1:
            if verbose:
                print ("Counter Instawin at", instalose)
            return instalose

        # 3. Minimax
        minimax = self.minimax(player,depth)
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




# helper lists of possible 4-cell lines for checking winner/scores
def genSlots():
    wSlots = []
    #horisontal
    for i in range(6):
        for j in range(4):
            line = []
            for k in range(4):
                line.append(i*7+j+k)
            wSlots.append(line)
    #vertical
    for i in range(7):
        for j in range(3):
            line=[]
            for k in range(4):
                line.append((i+j*7+k*7))
            wSlots.append(line)
    #diagonal falling
    for i in range(3):
        for j in range(4):
            line=[]
            for k in range(4):
                line.append((i*7+j+k*7+k))
            wSlots.append(line) 
    #diagonal rising
    for i in range(3,6):
        for j in range(4):
            line=[]
            for k in range(4):
                line.append((i*7+j-k*7+k))
            wSlots.append(line) 
    return wSlots

def genSlotsByCell():
    out = {}
    for i in range(42):
        out[i]=[]
        for line in wSlots:
            if i in line:
                line_shorten=line.copy()
                line_shorten.remove(i)
                out[i].append(line_shorten)
    return out

# Init helper lists
wSlots = genSlots()
wSlotsByCells = genSlotsByCell()






if __name__ == "__main__":
    
    import random
    import time
    random.seed(0)
    
    g=ConfState()
    player = 1

    while len(g.legitMoves())>0 and g.winner()=="":

        t = time.time()
        
        move = g.chooseMove(player, verbose=True)
        g.makeMove(player, move )

        print("="*20, g.pliesMade(), "="*20)
        #print ("Player", "X" if player==1 else "0", "goes:", move)
        print (g)
        
        player *=-1

        print (time.time()-t)
    print (g.winner() if g.winner()!="" else "no one", "won")





