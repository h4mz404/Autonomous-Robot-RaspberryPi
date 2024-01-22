#Importing packages
import cv2
import RPi.GPIO as gpio
import time
import numpy as np
from Utils.motion import *
from Utils.email import *
from Utils.sonar import *
from Utils.imu import *
from Utils.localization import *

# Define the parameters
object_height = 6   # Height of the object in cm
sensor_height = 2.76  # Height of the camera sensor in mm
focal_length = 3.04  # Focal length of the camera lens in mm
image_height = 480  # Height of the image captured by the camera in pixels
pixel_size = 0.0014  # Pixel size of the camera in mm

img_x, img_y = 320,240

def get_frame():
    #cap = cv2.VideoCapture(-1, cv2.CAP_V4L)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(0.01)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
    ret,frame=cap.read()
    frame = cv2.flip(frame,-1)
    cap.release()    
    return ret,frame

def analyze_frame(img,color):
    #img_x,img_y = int(img.shape[1]/2),int(img.shape[0]/2)
    img = cv2.line(img,(int(img_x-40),int(img_y)),(int(img_x+40),int(img_y)),(0,0,0),1)
    img = cv2.line(img,(int(img_x),int(img_y-40)),(int(img_x),int(img_y+40)),(0,0,0),1)
    color_lower = np.array([[150,80,35],[40,40,0],[90,110,0]])
    color_upper = np.array([[179,255,255],[90,255,255],[120,255,255]])
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV) 
    mask = cv2.inRange(hsv,color_lower[color],color_upper[color])
    #masked_img = cv2.bitwise_and(img,img,mask=mask)
    contours,_=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    foundBlock = 0
    center = 0
    h = 0
    if contours:
        #areas = [cv2.contourArea(c) for c in contours]
        #max_index = np.argmax(areas)
        #cnt=contours[max_index]
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        if area>200:
            foundBlock = 1
            x, y, w, h = cv2.boundingRect(cnt)
            center = (int((x+x+w)/2),int((y+y+h)/2))
            cv2.rectangle(img, (x,y),(x+w,y+h), (0,0,255), 3)
            cv2.circle(img,center,1,(255,0,0),2)
            print(center,area)
    return img,center,h,foundBlock

def orientOnBlock(pos,y_val):
    print('\nOrienting on Block')
    diff = y_val - img_x 
    #FOV = 38.88, FOV/640 = 0.061 
    rotation = diff * 0.061
    if rotation>4:
        #key_input('d',abs(rotation))
        pivotright(abs(rotation))
        pos = calcNewPos(pos,0,'r')
    elif rotation<-4:
        #key_input('a',abs(rotation))
        pivotleft(abs(rotation))
        pos = calcNewPos(pos,0,'r')
    return pos

def goToBlock(newPos,center,h):
    print('\nGoing towards block')
    BlockGrab = 0
    gripper_open()
    # Calculate the distance of the object
    distance = ((object_height * focal_length * image_height) / (h * sensor_height)) - 10
    print(f'\nBlock is {distance} cm away')
    if distance<30:
        if center[1]>350:
            #key_input('w',10)
            forward(10)
            gripper_close()
            print('Gripper Close')
            #key_input('a',90)
            newPos = calcNewPos(newPos,15,'w')
            BlockGrab = 1
        else:
            #key_input('w',10)
            forward(10)
            newPos = calcNewPos(newPos,10,'w')
    elif distance<60 and distance>29:
        #key_input('w',25)
        forward(25)
        newPos = calcNewPos(newPos,25,'w')
    elif distance>60:
        key_input('w',0.8*distance)
        newPos = calcNewPos(newPos,0.8*distance,'w')
    return newPos, BlockGrab

def checkIfDropZone(newPos,goalPos):
    if not (abs(newPos[0]-goalPos[0])<=5 and abs(newPos[1]-goalPos[1])<=5):
        newPos = goToDropZone(newPos,goalPos)
    return newPos

if __name__ == "__main__":
    t1 = time.time()
    startNode = [270,30,0]
    goalNode = [50,50]
    searchPos = [[90,90,10],[100,100,325],[210,100,300],[210,150,295]] # Chnage these
    searchAngles = [335,0,25]
    p,b,s = 0,0,0
    #Initialize Serial Port and PWM Pins
    print('\n-------->Program Start<--------')
    print('\n-------->Initializing Serial and GPIO pins<--------')
    init()
    print('\n-------->Current Parameters<--------')
    print('Gripper: Closed')
    startNode[2] = getYaw()
    print('\nCurrent Position: ',startNode)
    newPos = startNode
    print('\n-------->Script Start<--------')
    color ={0:'Red',1:'Green',2:'Blue'}
    mask = [0,1,2,0,1,2,0,1,2]
    blockGrab = 0
    txtfilename = 'positiondata_'+str(time.time())+'.txt'
    f = open(txtfilename,'a')
    try: 
        while True:
            ti_1 = time.time()
            ret,frame = get_frame()
            if ret==True:
                #newPos = calcNewPos(newPos)
                data = str(newPos)+'\n'
                f.write(data)
                foundBlock,h,center = 0,0,0
                img,center,h,foundBlock = analyze_frame(frame,mask[b])
                if foundBlock:
                    '''cv2.imshow("Contours Detected",img)
                    cv2.waitKey(1)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break'''
                    p = 0
                    print(f'Block Found is {color[mask[b]]}')
                    #After grabbing block
                    if blockGrab:
                        print(f'\n{color[mask[b]]} Block Grabbed')
                        #Send Email
                        sendPicEmail(color[mask[b]],frame)
                        newPos = goToDropZone(newPos,goalNode)
                        newPos = checkIfDropZone(newPos,goalNode)
                        print(f'\n{color[mask[b]]} Block Dropped Successfully')
                        if b%2 == 0: newPos = reOrient(newPos)
                        blockGrab = 0
                        newPos = go2Pos(newPos,searchPos[0])
                        b +=1
                        print(f'\nNext block is {color[mask[b]]}')
                        if b == 9: b=0
                        continue
                    else:
                        newPos = orientOnBlock(newPos,center[0])
                        newPos, blockGrab = goToBlock(newPos,center,h)
                else:
                    #If block not found
                    s = go2SearchAngle(s)
                    if s == 3:
                        s = 0
                        p +=1
                        if p == len(searchPos)-1: p = 1 
                        newPos = go2Pos(newPos,searchPos[p]) 
                    print('Searching for object....')
                    continue
            else:
                print('Camera Fail')
                break
            ti2 = time.time()
            print('\nTime for each iteratiion', ti2-ti_1)
            
    except KeyboardInterrupt:
        print('\n-------->Interrupt detected<--------')
    finally:
        t2 = time.time()
        print('\nRuntime: ',t2-t1,' seconds')
        print('\n-------->Cleaning up pins<--------')
        gameover()
        gpio.cleanup()
        cv2.destroyAllWindows()
        f.close()
        print('\n-------->Cleaning up successful<--------')
        print('\n-------->Program End<--------')
    



