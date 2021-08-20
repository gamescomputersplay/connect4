# Connect Four Module usage example

import connectfour

#Create new position from a string
# string should be 42-characters long, with X and 0 for played disks
position=connectfour.ConfState(  \
                "       "+\
                "       "+\
                "       "+\
                "   0   "+\
                "   X   "+\
                "  X00  ")

# This function returns the next column to make a move to (0-based)
# parameters are:
#- player (1 for X, -1 for 0)
#- depth to go in minimax algorithm

move = position.chooseMove( 1, 4 )

print ( "Next move is in the column", move )


