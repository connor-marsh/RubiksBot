import kociemba
import serial.tools.list_ports
from time import sleep


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
    
            
solvedState = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
cubeState = "LDDFUUFDUBBRLRRLRFDRRUFBUFBRDDBDUBDUBLLLLFRRFFBUFBULLD" # short state
cubeState = "UUFUUUUDBRRRRRRRFDFRUFFFDFFRDDDDUDDFLBLLLLLLBULBBBBLBB" # overall good state
cubeState = "FDBRUDUBBDRUURBUDBLRRLFFULFFDRFDBDLDRUBBLFFRLRFDUBLLUL" # long solution
cubeState = "BDURUBUFRBDFDRULURBUDLFLFFUDDBRDRFLFLBRFLUUFLRRDBBLDBL"
# inverse solution to ^: "U2 R L B R' U' D' R' U2 L2 B L2 U' L2 U L2 D R2 L2 F2 D"
solution = kociemba.solve(cubeState)
#solution = kociemba.solve(solvedState, cubeState) # inverse solution

#sampleSolution = "U' L D' B D' F L' B' U' F R' D F2 R2 D2 F2 D' L2 U D L2"
#sampleSolution = "F U F R' F2 R' D' L2 F' R' L B2 D' L2 F2 D2 R2 B2 D2 R2 U"
#sampleMoves = removeU(sampleSolution)

#solution = sampleSolution
print(solution)
moves = removeU(solution)
print(moves)
moves = collapseRedundantMoves(moves)
print(moves)


command1 = moves[0:int(len(moves)/2)] + "\n"
command2 = moves[int(len(moves)/2):] + "\n"

serialInst.write(command1.encode('utf-8'))
serialInst.readline() # wait for arduino to say it finished first sequence
#print("First half done")
serialInst.write(command2.encode('utf-8'))
serialInst.close()
