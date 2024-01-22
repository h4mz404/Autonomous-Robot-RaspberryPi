import math
import numpy as np
from Utils.imu import *
from Utils.motion import *
from Utils.sonar import *

startNode = [270,30,0]
goalNode = [50,50]

def calcNewPos(oldPosition,distance=0,action = 'q'):
    angleDegrees = getYaw()
    angleRadians = math.radians(angleDegrees)
    if action =='w': distance = distance
    elif action =='s': distance = -distance
    else: distance = 0
    #print(distance)
    x = oldPosition[0] + distance * math.sin(angleRadians)
    y = oldPosition[1] + distance * math.cos(angleRadians)
    newPos = (x, y, angleDegrees)
    print('>>>New Position is: ', newPos)
    return newPos

def go2Pos(curPos,goalPos = [100,100,0]):
    print(f'\nGoing to position {goalPos}')
    xDiff = goalPos[0]-curPos[0]
    yDiff = goalPos[1]-curPos[1]
    goalOrient = math.degrees(math.atan2(xDiff, yDiff))
    dist = (xDiff**2 + yDiff**2)**0.5
    rotation = goalOrient - curPos[2] 
    if rotation > 180: rotation -= 360
    elif rotation < -180: rotation += 360
    if rotation>0:
        #key_input('d',abs(rotation))
        pivotright(abs(rotation))
    elif rotation<0:
        #key_input('a',abs(rotation))
        pivotleft(abs(rotation))
    #key_input('w',dist)
    forward(dist)
    #print('Distance, Rotation: ',dist,rotation)
    newPos = calcNewPos(curPos,dist,'w')
    turn2Ang(goalPos[2])
    newPos = calcNewPos(newPos,dist,'d')
    return newPos

def go2Goal(curPos,goalPos = [30,30]):
    print(f'\nGoing to Goal position {goalPos}')
    xDiff = goalPos[0]-curPos[0]
    yDiff = goalPos[1]-curPos[1]
    goalOrient = math.degrees(math.atan2(xDiff, yDiff))
    dist = (xDiff**2 + yDiff**2)**0.5
    rotation = goalOrient - curPos[2] 
    if rotation > 180:
        rotation -= 360
    elif rotation < -180:
        rotation += 360
    if rotation>0:
        #key_input('d',abs(rotation))
        pivotright(abs(rotation))
    elif rotation<0:
        #key_input('a',abs(rotation))
        pivotleft(abs(rotation))
    #key_input('w',dist)
    forward(dist)
    print('Distance, Rotation: ',dist,rotation)
    newPos = calcNewPos(curPos,dist,'w')
    return newPos

def goToDropZone(curPos,goalPos = [50,50]):
    print(f'\nGoing to Drop Zone: {goalPos}')
    #newPos = go2Goal(curPos,goalPos)
    #print(f'\nGoing to Goal position {goalPos}')
    xDiff = goalPos[0]-curPos[0]
    yDiff = goalPos[1]-curPos[1]
    goalOrient = math.degrees(math.atan2(xDiff, yDiff))
    dist = (xDiff**2 + yDiff**2)**0.5
    rotation = goalOrient - curPos[2] 
    if rotation > 180:
        rotation -= 360
    elif rotation < -180:
        rotation += 360
    if rotation>0:
        #key_input('d',abs(rotation))
        pivotright(abs(rotation))
    elif rotation<0:
        #key_input('a',abs(rotation))
        pivotleft(abs(rotation))
    #key_input('w',dist)
    forward(dist)
    print('Distance, Rotation: ',dist,rotation)
    #newPos = calcNewPos(curPos,dist,'w')
    gripper_close()
    gripper_open()
    reverse(18)
    dist = dist-18
    newPos = calcNewPos(curPos,dist,'w')
    return newPos

def turn2Ang(goalAngle):
    print(f'\nTurning to Angle {goalAngle}')
    rotation = goalAngle - getYaw()
    if rotation > 180:
        rotation -= 360
    elif rotation < -180:
        rotation += 360
    if rotation>0:
        print('Left')
        pivotright(abs(rotation))
    elif rotation<0:
        print('Right')
        pivotleft(abs(rotation))

def reOrient(pos):
    print(f'\nReOrient at DropZone {pos}')
    turn2Ang(270)
    time.sleep(1)
    x = avg_dist()
    print('\n X:',x)
    turn2Ang(180)
    time.sleep(1)
    y = avg_dist()
    print('\n Y:',y)
    if not isinstance(x,float):x = pos[0]
    if not isinstance(y,float):y = pos[1]
    newPos = (x,y,getYaw())
    print('>>>Re-Oriented Position is: ', newPos)
    return newPos

def go2SearchAngle(i):
    searchAngles = [25,50,75,90,295,335,0]
    turn2Ang(searchAngles[i])
    i+=1
    return i

