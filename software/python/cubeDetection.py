import cv2
import numpy as np
from math import sqrt
from copy import deepcopy
import os

cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
outWidth = 240 # this number should be threeven for simplicity sake

#pts for cube borders
# also pls dont judge me for making these two separate variables it was just faster to use
# with open cv calls. I know its a bad method

alternatePics = False
pts1 = []
pts1file = 'cubePts1.txt' if not alternatePics else 'cubePts3.txt'
pts2 = []
if os.path.exists(pts1file):
    with open(pts1file, 'r') as file:
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


selectedPoint = [-1,-1] #first index is pts1 or pts2, second index is which point

def handle_mouse(event,x,y,flags,param):
    global mouseX,mouseY, selectedPoint
    if event == cv2.EVENT_LBUTTONDBLCLK:
        mouseX,mouseY = x,y
        if selectedPoint == [-1,-1]:
            #find closest point to mouse
            shortestDist = 999999
            shortestIndex = 0
            shortestList = 0 #to choose pts1 or pts2
            for i in range(len(pts1)):
                curDist = sqrt(pow(mouseX - pts1[i][0], 2) + pow(mouseY - pts1[i][1], 2))
                if curDist < shortestDist:
                    shortestDist = curDist
                    shortestIndex = i
                    shortestList = 0

                curDist = sqrt(pow(mouseX - pts2[i][0], 2) + pow(mouseY - pts2[i][1], 2))
                if curDist < shortestDist:
                    shortestDist = curDist
                    shortestIndex = i
                    shortestList = 1
            selectedPoint = [shortestList, shortestIndex]

            
        else:
            #move selected point to current pos
            if selectedPoint[0] == 0:
                pts1[selectedPoint[1]] = [mouseX, mouseY]
            else:
                pts2[selectedPoint[1]] = [mouseX, mouseY]
            selectedPoint = [-1,-1]
        

while cap.isOpened():
    success, img = cap.read()
    rows, cols, channels = img.shape
    imgCenterIndex = (int(rows/2),int(cols/2))
    imgCenter = (int(cols/2),int(rows/2))
    temp=deepcopy(img[imgCenterIndex])
    img[imgCenterIndex]=(0,0,255)


    

    
    cv2.line(img, pts1[0], pts1[1], (255, 0, 0), 1)
    cv2.line(img, pts1[1], pts1[3], (255, 0, 0), 1)
    cv2.line(img, pts1[3], pts1[2], (255, 0, 0), 1)
    cv2.line(img, pts1[2], pts1[0], (255, 0, 0), 1)

    cv2.line(img, pts2[0], pts2[1], (0, 255, 0), 1)
    cv2.line(img, pts2[1], pts2[3], (0, 255, 0), 1)
    cv2.line(img, pts2[3], pts2[2], (0, 255, 0), 1)
    cv2.line(img, pts2[2], pts2[0], (0, 255, 0), 1)

    # convert to format needed for cv transform
    pts1np = np.float32(pts1)
    pts2np = np.float32(pts2)
    outPtsnp = np.float32([[0,0],[outWidth,0],[0,outWidth],[outWidth,outWidth]])
    
    M_UP = cv2.getPerspectiveTransform(pts1np,outPtsnp)
    dstUp = cv2.warpPerspective(img,M_UP,(outWidth,outWidth))
    M_FRONT = cv2.getPerspectiveTransform(pts2np,outPtsnp)
    dstFront = cv2.warpPerspective(img,M_FRONT,(outWidth,outWidth))
    
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue


    
    cv2.imshow('Video Stream', img)
    cv2.setMouseCallback('Video Stream',handle_mouse)
    cv2.imshow("Upper Face", dstUp)
    cv2.imshow("Front Face", dstFront)
    img[imgCenterIndex]=temp
    if cv2.waitKey(1) == ord(' '):
        break
cap.release()
cv2.destroyAllWindows()

with open(pts1file, 'w') as file:
    for row in pts1:
        # Join the elements of each row with a space and write to the file
        file.write(' '.join(map(str, row)) + '\n')
with open('cubePts2.txt', 'w') as file:
    for row in pts2:
        # Join the elements of each row with a space and write to the file
        file.write(' '.join(map(str, row)) + '\n')

# for sampling HLS values (camera tuning basically)
#img = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
#dstFront = cv2.cvtColor(dstFront, cv2.COLOR_BGR2HLS)
#dstUp = cv2.cvtColor(dstUp, cv2.COLOR_BGR2HLS)
print(img[imgCenterIndex])

#flip distorted images to make sense with human perception
dstFront = cv2.flip(dstFront, 1)
dstUp = cv2.flip(cv2.flip(dstUp, 1), 0)

tileWidth = int(outWidth/3)
tileOffset = int(tileWidth/3)
tileFrontMeanImg = np.zeros((3,3,3))
tileUpMeanImg = np.zeros((3,3,3))
for i in range(3):
    for j in range(3):
        tileFrontImg = dstFront[i*tileWidth+tileOffset:(i+1)*tileWidth-tileOffset,j*tileWidth+tileOffset:(j+1)*tileWidth-tileOffset]
        #cv2.line(dstFront, (i*tileWidth+tileOffset,j*tileWidth+tileOffset), ((i+1)*tileWidth-tileOffset,(j+1)*tileWidth-tileOffset), 0, 3)
        tileFrontMean = np.mean(tileFrontImg, (0,1))
        tileFrontMeanImg[i,j] = tileFrontMean
        
        tileUpImg = dstUp[i*tileWidth+tileOffset:(i+1)*tileWidth-tileOffset,j*tileWidth+tileOffset:(j+1)*tileWidth-tileOffset]
        #cv2.line(dstUp, (i*tileWidth+tileOffset,j*tileWidth+tileOffset), ((i+1)*tileWidth-tileOffset,(j+1)*tileWidth-tileOffset), 0, 3)
        tileUpMean = np.mean(tileUpImg, (0,1))
        tileUpMeanImg[i,j] = tileUpMean
tileFrontMeanImg = tileFrontMeanImg.astype(np.uint8)
tileUpMeanImg = tileUpMeanImg.astype(np.uint8)

#RGB VALUES
yellow = np.asarray((134,235,215))
#white = np.asarray((210, 210, 210))
white = np.asarray((999, 999, 999)) # to make it not detect white w MSA
red = np.asarray((55, 45, 155))
green = np.asarray((100, 140, 80))
blue = np.asarray((145, 71, 24))
orange = np.asarray((40, 122, 208))

"""#HLS VALUES
yellow = np.asarray((36,173,202))
white = np.asarray((10000, 226, 255)) # H is irrelevant for white kinda
red = np.asarray((160, 80, 210))
green = np.asarray((62, 122, 66))
blue = np.asarray((110, 68, 218))
orange = np.asarray((13, 129, 162))"""


colors = np.asarray([white, yellow, green, blue, orange, red])
colorNames = ["white", "yellow", "green", "blue", "orange", "red"]
colorsMsa = np.zeros(6)
whiteLightnessThreshold = 145
whiteSaturationThreshold = 70
frontColors = []
upColors = []
hlsFront = cv2.cvtColor(tileFrontMeanImg, cv2.COLOR_BGR2HLS)
hlsUp = cv2.cvtColor(tileUpMeanImg, cv2.COLOR_BGR2HLS)
print(hlsFront)
print(hlsUp)
for i in range(3):
    frontColors.append([])
    upColors.append([])
    for j in range(3):
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

        colorsMsa = np.sqrt(np.mean(np.square(np.full((6,3), tileFrontMeanImg[i,j])-colors), axis=1))
        index = np.argmin(colorsMsa)
        frontColors[i].append(colorNames[index])
        
        if frontColors[i][j] == "red" or frontColors[i][j] == "orange" or frontColors[i][j] == "yellow" or frontColors[i][j] == "green":
            if hlsFront[i,j,0] > 0 and hlsFront[i,j,0] < 18:
                frontColors[i][j] = "orange"
            elif hlsFront[i,j,0] >= 18 and hlsFront[i,j,0] < 46:
                frontColors[i][j] = "yellow"
            elif hlsFront[i,j,0] >= 46 and hlsFront[i,j,0] < 85:
                frontColors[i][j] = "green"
            else:
                frontColors[i][j] = "red"
        if hlsFront[i,j,1] > whiteLightnessThreshold:# and hlsFront[i,j,2] < whiteSaturationThreshold:
            frontColors[i][j] = "white"
            
        
        
        colorsMsa = np.sqrt(np.mean(np.square(np.full((6,3), tileUpMeanImg[i,j])-colors), axis=1))
        index = np.argmin(colorsMsa)
        upColors[i].append(colorNames[index])
        
        if upColors[i][j] == "red" or upColors[i][j] == "orange" or upColors[i][j] == "yellow" or upColors[i][j] == "green":
            if hlsUp[i,j,0] > 0 and hlsUp[i,j,0] < 18:
                upColors[i][j] = "orange"
            elif hlsUp[i,j,0] >= 18 and hlsUp[i,j,0] < 50:
                upColors[i][j] = "yellow"
            elif hlsUp[i,j,0] >= 46 and hlsUp[i,j,0] < 85:
                upColors[i][j] = "green"
            else:
                upColors[i][j] = "red"
        if hlsUp[i,j,1] > whiteLightnessThreshold:# and hlsUp[i,j,2] < whiteSaturationThreshold:
            upColors[i][j] = "white"

print(frontColors)
print(upColors)


#cv2.imshow('Front Mean', cv2.cvtColor(dstFront, cv2.COLOR_HLS2BGR))
#cv2.imshow('Up Mean', cv2.cvtColor(dstUp, cv2.COLOR_HLS2BGR))
cv2.imshow('Front Mean', dstFront)
cv2.imshow('Up Mean', dstUp)
cv2.waitKey(0)



cv2.destroyAllWindows()
