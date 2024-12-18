import kociemba

#side order is URFDLB
upSide = [['green', 'white', 'blue'], ['green', 'yellow', 'yellow'], ['blue', 'orange', 'white']]
frontSide = [['red', 'green', 'blue'], ['red', 'red', 'orange'], ['orange', 'red', 'yellow']]
rightSide = [['orange', 'orange', 'red'], ['white', 'green', 'blue'], ['green', 'yellow', 'blue']]
#downSide = [['white', 'yellow', 'red'], ['red', 'white', 'green'], ['green', 'blue', 'yellow']] # unknown side
downSide = [['','',''],['','',''],['','','']]
leftSide = [['yellow', 'white', 'white'], ['yellow', 'blue', 'white'], ['red', 'green', 'green']]
backSide = [['yellow', 'blue', 'orange'], ['red', 'orange', 'blue'], ['orange', 'orange', 'white']]
upSideLRTurned = [['white', 'white', 'red'], ['red', 'yellow', 'green'], ['green', 'orange', 'yellow']]
upSideFBTurned = [['yellow', 'blue', 'green'], ['green', 'yellow', 'yellow'], ['red', 'yellow', 'white']]


# get bottom color from top color
topColor = upSide[1][1]
bottomColor = ""
if topColor == 'white':
    bottomColor = 'yellow'
elif topColor == 'yellow':
    bottomColor = 'white'
elif topColor == 'red':
    bottomColor = 'orange'
elif topColor == 'orange':
    bottomColor = 'red'
elif topColor == 'green':
    bottomColor = 'blue'
elif topColor == 'blue':
    bottomColor = 'green'
downSide[1][1] = bottomColor
# get bottom side from alternate 2 pictures of top sides
downSide[0][0] = upSideLRTurned[0][0]
downSide[1][0] = upSideLRTurned[1][0]
downSide[2][0] = upSideLRTurned[2][0]
downSide[0][2] = upSideLRTurned[0][2]
downSide[1][2] = upSideLRTurned[1][2]
downSide[2][2] = upSideLRTurned[2][2]
downSide[0][1] = upSideFBTurned[2][1]
downSide[2][1] = upSideFBTurned[0][1]

# get bottom side from 5 other sides (not always possible!)
# NEVERMIND I decided not to do this and just turn the sides to see bottom pieces (shoutout johnny)
# but leaving the start of the code below in quotes in case I want to use it at some point
"""bottomCorners = [] # order is DFR, DFL, DBL, DBR
if frontSide[2][2] == 'white':
    if rightSide[2][0] == 'red':
        bottomCorners.append('green')
    elif rightSide[2][0] == 'orange':
        bottomCorners.append('blue')
    elif rightSide[2][0] == 'blue':
        bottomCorners.append('red')
    elif rightSide[2][0] == 'green':
        bottomCorners.append('orange')"""

# get kociemba cube state string from 6 sides
sides = [upSide, rightSide, frontSide, downSide, leftSide, backSide]
sideColors = [side[1][1] for side in sides]
sideNames = ['U', 'R', 'F', 'D', 'L', 'B']
cubeState = ""
for side in sides:
    for row in side:
        for col in row:
            cubeState += sideNames[sideColors.index(col)]

print(cubeState)
print(kociemba.solve(cubeState))
