import kociemba
import serial.tools.list_ports
from time import sleep
import cv2
import numpy as np
from math import sqrt
from copy import deepcopy
import os

# Serial setup stuff
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()
portsList = []

for one in ports:
    portsList.append(str(one))
    print(str(one))

serialInst.baudrate = 115200
serialInst.port = "COM9"
serialInst.open()



print("Sleeping to allow time for Serial to connect")
sleep(8)
print("Done sleeping")

def runMoves(moves):
    serialInst.write((moves+"\n").encode('utf-8'))
    serialInst.readline() #wait for completion

# some solve string manipulation stuff
def removeU(moves):
    output = ""
    prevU = False
    counter = 0
    for move in moves:
        counter+=1
        if move == "U":
            if counter == len(moves):
                output += "R L F2 B2 R' L' D R L F2 B2 R' L'"
            else:
                prevU = True
                continue
        elif prevU:
            prevU = False
            if move == " ":
                output += "R L F2 B2 R' L' D R L F2 B2 R' L' "
            elif move == "'":
                output += "R L F2 B2 R' L' D' R L F2 B2 R' L'"
            else:
                # half turn
                output += "R L F2 B2 R' L' D2 R L F2 B2 R' L'"
        else:
            output += move
    return output
def collapseRedundantMoves(moves):
    moveList = moves.split(" ")
    output = recurseCollapse(moveList)
    return " ".join(output)
oppositeMoves = {
    "R":"L",
    "L":"R",
    "F":"B",
    "B":"F",
    "U":"D",
    "D":"U"
}
def recurseCollapse(moveList):
    newList = []
    collapsed = False
    i = 0
    while i < len(moveList): # doing C style for loop to allow for skipping multiple iterations easier
        if i < len(moveList)-1 and moveList[i][0] == moveList[i+1][0]: # if two consecutive moves turn the same side
            collapsed = True # We can collapse
            if len(moveList[i])==1:
                angle1 = 90
            elif moveList[i][1]=='2':
                angle1 = 180
            else:
                angle1 = -90
            if len(moveList[i+1])==1:
                angle2 = 90
            elif moveList[i+1][1]=='2':
                angle2 = 180
            else:
                angle2 = -90
            if angle1+angle2 == 90: #normal clockwise move
                newList.append(moveList[i][0])
            elif angle1+angle2 == 180: # half turn
                newList.append(moveList[i][0]+'2')
            elif (angle1+angle2)%360 == 270: # counterclockwise
                newList.append(moveList[i][0]+"'")
            # note that if angle1+angle2 == 0 then we do nothing and those 2 moves disappear
            i += 1 # increment i to skip over the next 1 items
        # check if two moves that turn the same side sandwich a move that turns the opposite side
        
        elif i < len(moveList)-2 and moveList[i][0] == moveList[i+2][0] and moveList[i][0] == oppositeMoves[moveList[i+1][0]]:
            collapsed = True # We can collapse
            if len(moveList[i])==1:
                angle1 = 90
            elif moveList[i][1]=='2':
                angle1 = 180
            else:
                angle1 = -90
            if len(moveList[i+2])==1:
                angle2 = 90
            elif moveList[i+2][1]=='2':
                angle2 = 180
            else:
                angle2 = -90
            if (angle1+angle2)%360 == 90: #normal clockwise move
                newList.append(moveList[i][0])
            elif (angle1+angle2)%360 == 180: # half turn
                newList.append(moveList[i][0]+'2')
            elif (angle1+angle2)%360 == 270: # counterclockwise
                newList.append(moveList[i][0]+"'")
            # note that if angle1+angle2 == 0 then we do nothing and those 2 moves disappear
            newList.append(moveList[i+1]) # make sure to add the sandwiched moves
            i += 2 # increment i to skip over the next 2 items
        else:
            newList.append(moveList[i])
        i += 1
    if collapsed:
        return recurseCollapse(newList)
    else:
        return moveList # if no collapse then moveList=newList

# CV setup stuff
cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
outWidth = 240 # this number should be threeven for simplicity sake

#pts for cube borders
# also pls dont judge me for making these two separate variables it was just faster to use
# with open cv calls. I know its a bad method

pts1 = []
pts2 = []
pts3 = []
if os.path.exists('cubePts1.txt'):
    with open('cubePts1.txt', 'r') as file:
        for line in file:
            # Convert each line to a list of integers and append it to read_list
            pts1.append(list(map(int, line.split())))
else:
    pts1 = [[530, 260],[148, 260],[480, 33],[188, 33]] # default pts1

if os.path.exists('cubePts2.txt'):
    with open('cubePts2.txt', 'r') as file:
        for line in file:
            # Convert each line to a list of integers and append it to read_list
            pts2.append(list(map(int, line.split())))
else:
    pts2 = [[530, 270],[148, 270],[475, 460],[186, 450]] # default pts2

if os.path.exists('cubePts3.txt'):
    with open('cubePts3.txt', 'r') as file:
        for line in file:
            # Convert each line to a list of integers and append it to read_list
            pts3.append(list(map(int, line.split())))
else:
    pts3 = [[283, 279],[59, 120],[493, 118],[279, 0]] # default pts3

print("Hello! I'm a rubik's cube solving robot, nice to meetcha!")
while True:
    #Physical Setup instructions for user
    print("Please insert cube into bottom motor cube turner, and align it to be square")
    input("Hit enter when done:")
    print("Make sure the four equator motors are pulled out to the edge of the board")
    input("Hit enter when done:")
    print("Taking initial pictures...")
    timer = 0
    images = []
    while True:
        _, img = cap.read()
        if timer == 0:
            runMoves("D0")
        elif timer == 100:
            images.append(img)
            runMoves("D")
        elif timer == 200:
            images.append(img)
            runMoves("D")
        elif timer == 300:
            images.append(img)
            runMoves("D")
        elif timer == 400:
            images.append(img)
            runMoves("D0")
        elif timer == 500:
            break
        timer+=10
        sleep(0.01)
        #cv2.imshow('Video Stream', img)
        if cv2.waitKey(1) == ord(' '):
            break

    print("Done!")
    print("Please push in the four equator motors and make sure they are properly aligned and well fitted into the cube")
    input("Hit enter when done:")
    print("Taking alternate pictures...")
    timer = 0
    while True:
        _, img = cap.read()
        if timer == 0:
            runMoves("R2 L2")
        elif timer == 200:
            images.append(img)
            runMoves("F2 B2")
        elif timer == 400:
            images.append(img)
            runMoves("F2 B2 R2 L2")
        elif timer == 600:
            break
        timer+=10
        sleep(0.01)
        #cv2.imshow('Video Stream', img)
        if cv2.waitKey(1) == ord(' '):
            break

    print("Done!")
    print("Analyzing pictures...")

    pts1np = np.float32(pts1)
    pts2np = np.float32(pts2)
    pts3np = np.float32(pts3)
    outPtsnp = np.float32([[0,0],[outWidth,0],[0,outWidth],[outWidth,outWidth]])
        
    M_UP = cv2.getPerspectiveTransform(pts1np,outPtsnp)
    M_FRONT = cv2.getPerspectiveTransform(pts2np,outPtsnp)
    M_ALT = cv2.getPerspectiveTransform(pts3np,outPtsnp)

    dstImgs = []
    for i in range(len(images)): # also note that flipping images over x and y accordingly to make sense with our perception
        if i == 0: # first image grab front and top side
            dstImgs.append(cv2.flip(cv2.flip(cv2.warpPerspective(images[i],M_UP,(outWidth,outWidth)), 1), 0))
            dstImgs.append(cv2.flip(cv2.warpPerspective(images[i],M_FRONT,(outWidth,outWidth)),1))
        elif i == 4 or i == 5: # final 2 images use the alternate transform
            dstImgs.append(cv2.flip(cv2.flip(cv2.warpPerspective(images[i],M_ALT,(outWidth,outWidth)), 1), 0))
        else: # next 3 images just grab front
            dstImgs.append(cv2.flip(cv2.warpPerspective(images[i],M_FRONT,(outWidth,outWidth)),1))


    tileWidth = int(outWidth/3)
    tileOffset = int(tileWidth/2.8)
    tileMeanImgs = [np.zeros((3,3,3)) for i in range(7)]
    tileFrontMeanImg = np.zeros((3,3,3))
    tileUpMeanImg = np.zeros((3,3,3))
    for index in range(len(dstImgs)):
        for i in range(3):
            for j in range(3):
                tileImg = dstImgs[index][i*tileWidth+tileOffset:(i+1)*tileWidth-tileOffset,j*tileWidth+tileOffset:(j+1)*tileWidth-tileOffset]
                cv2.line(dstImgs[index], (i*tileWidth+tileOffset,j*tileWidth+tileOffset), ((i+1)*tileWidth-tileOffset,(j+1)*tileWidth-tileOffset), 0, 3)
                tileMean = np.mean(tileImg, (0,1))
                tileMeanImgs[index][i,j] = tileMean
        tileMeanImgs[index] = tileMeanImgs[index].astype(np.uint8)
    print(tileMeanImgs)
    hlsImgs = [cv2.cvtColor(rgbImg, cv2.COLOR_BGR2HLS) for rgbImg in tileMeanImgs]
    print(hlsImgs)
    #for i in range(len(dstImgs)):
        #cv2.imshow("img"+str(i),dstImgs[i])
    #cv2.waitKey(0)

    #RGB VALUES
    """yellow = np.asarray((134,235,215))
    white = np.asarray((190, 190, 190))
    #white = np.asarray((999, 999, 999)) # to make it not detect white w MSA
    red = np.asarray((55, 45, 155))
    green = np.asarray((100, 140, 80))
    blue = np.asarray((145, 71, 24))
    orange = np.asarray((40, 122, 208))"""

    """#HLS VALUES
    yellow = np.asarray((36,173,202))
    white = np.asarray((10000, 226, 255)) # H is irrelevant for white kinda
    red = np.asarray((160, 80, 210))
    green = np.asarray((62, 122, 66))
    blue = np.asarray((110, 68, 218))
    orange = np.asarray((13, 129, 162))"""


    #colors = np.asarray([white, yellow, green, blue, orange, red])
    #colorNames = ["white", "yellow", "green", "blue", "orange", "red"]
    #colorsMsa = np.zeros(6)
    #whiteLightnessThreshold = 145
    #whiteSaturationThreshold = 70

    tileColors = []
    redOrangePieces = []
    for index in range(len(tileMeanImgs)):
        tileColors.append([])
        for i in range(3):
            tileColors[index].append([])
            for j in range(3):
                tileColors[index][i].append("")
                """if tileFrontMeanImg[i,j,1]>whiteLightnessThreshold and tileFrontMeanImg[i,j,2]>whiteSaturationThreshold:
                    frontColors[i].append("white")
                else:
                    colorsMsa = np.abs(np.full((1,6), tileFrontMeanImg[i,j, 0])-colors[:,0])
                    index = np.argmin(colorsMsa)
                    frontColors[i].append(colorNames[index])
                
                
                if tileFrontMeanImg[i,j,1]>whiteLightnessThreshold and tileFrontMeanImg[i,j,2]>whiteSaturationThreshold:
                    upColors[i].append("white")
                else:
                    colorsMsa = np.abs(np.full((1,6), tileUpMeanImg[i,j, 0])-colors[:,0])
                    index = np.argmin(colorsMsa)
                    upColors[i].append(colorNames[index])"""
                
                #colorsMsa = np.sqrt(np.mean(np.square(np.full((6,3), tileMeanImgs[index][i,j])-colors), axis=1))
                #colorIndex = np.argmin(colorsMsa)
                #tileColors[index][i].append(colorNames[colorIndex])

                
                if hlsImgs[index][i][j][2] < 20: # if SUPER low saturation then always white
                    tileColors[index][i][j] = "white"
                #check if hue is in range where it could be blue or white
                # YES I know white can be ANY Hue, but this camera always picks it up as blue for some reason
                elif hlsImgs[index][i][j][0] >= 85 and hlsImgs[index][i][j][0] < 130:
                    if hlsImgs[index][i][j][2] < 70: # if low saturation then has to be white
                        tileColors[index][i][j] = "white"
                    elif hlsImgs[index][i][j][1] > 170: # if super high lightness then has to be white
                        tileColors[index][i][j] = "white"
                    else: # else blue
                        tileColors[index][i][j] = "blue"
                #if tileColors[index][i][j] == "red" or tileColors[index][i][j] == "orange" or tileColors[index][i][j] == "yellow" or tileColors[index][i][j] == "green":
                elif hlsImgs[index][i,j,0] > 1 and hlsImgs[index][i,j,0] < 18:
                    tileColors[index][i][j] = "orange"
                    redOrangePieces.append((int(hlsImgs[index][i][j][0]), (index,i,j))) # (hue, position)
                elif hlsImgs[index][i,j,0] >= 18 and hlsImgs[index][i,j,0] < 46:
                    tileColors[index][i][j] = "yellow"
                elif hlsImgs[index][i,j,0] >= 46 and hlsImgs[index][i,j,0] < 85:
                    tileColors[index][i][j] = "green"
                    if hlsImgs[index][i][j][1] > 250: # if super high lightness then its actually white
                        tileColors[index][i][j] = "white"
                else:
                    tileColors[index][i][j] = "red"
                    redOrangePieces.append((int(hlsImgs[index][i][j][0]), (index,i,j))) # (hue, position)
                #if hlsFront[i,j,1] > whiteLightnessThreshold:# and hlsFront[i,j,2] < whiteSaturationThreshold:
                    #frontColors[i][j] = "white"

    # Do additional processing to distinguish between red and orange
    # Assume every piece identified as red or orange is actually red or orange
    # Remove pieces from the list that are duplicates from the two alternate pictures
    invalidLocations = [(5, 0, 1), (5, 1, 1), (5, 2, 1), (6, 0, 0), (6, 0, 2), (6, 1, 0), (6, 1, 1), (6, 1, 2), (6, 2, 0), (6, 2, 2)]
    redOrangePieces = [piece for piece in redOrangePieces if piece[1] not in invalidLocations]
    # Sort them by hue 160 < 180 < 0 < 18
    redOrangePieces.sort(key=lambda x: x[0] if x[0] > 100 else x[0]+180)
    print(redOrangePieces)
    # Take the 8 or 9 lowest and call them red and the 8 or 9 highest and call them orange
    # only if the bottom center piece is red or orange
    for i in range(8 if len(redOrangePieces) == 17 else 9):
        loc = redOrangePieces[i][1]
        tileColors[loc[0]][loc[1]][loc[2]] = "red"
        loc = redOrangePieces[len(redOrangePieces)-1-i][1]
        tileColors[loc[0]][loc[1]][loc[2]] = "orange"
    # (either 1 or 0 remaining depending on bottom center tile being red or orange)
    # Any remaining piece is red if its closer to highest red piece or orange if its closer to lowest orange piece
    if len(redOrangePieces) == 17:
        loc = redOrangePieces[8][1]
        hueMiddle = redOrangePieces[8][0] if redOrangePieces[8][0] > 100 else redOrangePieces[8][0]+180
        hueUpper = redOrangePieces[9][0] if redOrangePieces[9][0] > 100 else redOrangePieces[9][0]+180
        hueLower = redOrangePieces[7][0] if redOrangePieces[7][0] > 100 else redOrangePieces[7][0]+180
        if (hueMiddle - hueLower) < (hueUpper - hueMiddle):
            tileColors[loc[0]][loc[1]][loc[2]] = "red"
        else:
            tileColors[loc[0]][loc[1]][loc[2]] = "orange"

    print(tileColors)

    cv2.destroyAllWindows()

    print("Done!")
    print("Assembling Cube State...")
    #side order is URFDLB
    upSide = tileColors[0]
    frontSide = tileColors[1]
    leftSide = tileColors[2]
    backSide = tileColors[3]
    rightSide = tileColors[4]
    upSideLRTurned = tileColors[5]
    upSideFBTurned = tileColors[6]
    downSide = [['','',''],['','',''],['','','']]

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

    print("Done!")
    print("Finding solution...")
    solution = kociemba.solve(cubeState)
    print(solution)
    moves = removeU(solution)
    moves = collapseRedundantMoves(moves)
    print(moves)
    print("Done!")
    print("Solving cube...")
    runMoves(moves[0:int(len(moves)/2)])
    print("First half done!")
    runMoves(moves[int(len(moves)/2):])

    print("Done!")
    goAgain = input("Do you want to solve another cube? (y/n)")
    if not (goAgain[0] == 'y' or goAgain[0] == 'Y'):
        break


print("Goodbye!")
serialInst.close()
cap.release()
