# Connect Four Module usage example

import connectfour

# Create new position from a string
# string should be 42-characters long, with X and 0 for played disks

position = connectfour.Connect4Board(
                "       " +
                "       " +
                "       " +
                "   0   " +
                "   X   " +
                "  X00  ")


# chooseMove function returns the next column to make a move to (0-based)
# Parameters:
#   player (1 for X, -1 for 0)
#   depth: plies to go through in minimax algorithm
#   verbose: if True display some results from how the algorithm

move = position.chooseMove(player=1, depth=4, verbose=True)

print (position)
print ("Next move is in the column", move)

