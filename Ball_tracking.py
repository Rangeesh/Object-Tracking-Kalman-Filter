# ---------------------------------------------------------------------------- #
# Course: MEEN 689 - Robotic Perception
# Instructor: Sr. Srikanth Saripalli
# Project: Object Tracking using Kalman Filters
# Code Brief: Object Detection in Camera Frame and World Frame
# Contributors: 
# Rangeesh - rangeesh@tamu.edu
# Jaikrishna - jk1@tamu.edu
# Riya - riyakhurana@tamu.edu
# Neelkamal - neel.sept18@tamu.edu
# ---------------------------------------------------------------------------- #


# ------------------------------ Importing Stuff ----------------------------- #
from collections import deque
from imutils.video import VideoStream
from statistics import mean, median
import numpy as np
import argparse
import cv2
import imutils
import time
import csv
# import urllib

# ---------------------------------------------------------------------------- #
#                                Hyperparameters                               #
# Moving Average Window - Reduce if frame rate is low
# UPDATE - Reduce if frame rate is low
MOVING_AVERAGE_WINDOW = 10
UPDATE = 1
RADIUS = 33.35/10 # cm, 'cause mm has too many m's
url = 'http://192.168.1.13:8888/shot.jpg'
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#                               CSV Files to see                               #
# ~/Desktop/hackeye/CSV
# xlist_csv.csv ylist_csv.csv rlist_csv.csv  --- Camera Coordinates
# 
# ---------------------------------------------------------------------------- #

# ------------------ Argument Parser - This is useless stuff ----------------- #
ap = argparse.ArgumentParser()
ap.add_argument("-v","--video", help = "Path to video file")
ap.add_argument("-b","--buffer",help="Size of deque")
args=vars(ap.parse_args) # So essentially, your arguments will be args["video"],args["buffer"]

# ---- Bounds for Green Color - Tune this if ball isn't getting detected ---- #
# Green Limits - Green Lower, Green Upper
# greenLower = (29,86,6) # TODO: Tune this -- use the range-detector script in the imutils module
greenLower = (38,80,15)
greenUpper = (64,255,255) # TODO: Tune this -- or do it manually - left Button gives a value kind of
# greenUpper = (76,100,100)
# pts = deque(maxlen=args["buffer"] ) # maxlen is an argument for the deque 'function'

# ----------- Length of that Red line - Change it if it's too much ----------- #
LEN = 64
pts = deque(maxlen=LEN)

# Uncomment incase you want to a live stream
# if not args.get("video", False):
#     vs = VideoStream(src=0).start()
# else:
#     vs = cv2.VideoCapture(args["video"])
# time.sleep(2.0) # For starting the camera - Warm up time

# Comment if you want to do a Live Stream
# vs = cv2.VideoCapture(args["Video"])

# ------------------------------ Video START -------------------------------- #
# vs = cv2.VideoCapture("/home/rangeesh/Desktop/hackeye/Videos/Full_video.mp4")
# vs = cv2.VideoCapture("/home/rangeesh/Desktop/hackeye/Videos/Movie_6.mp4")
vs = cv2.VideoCapture("/home/rangeesh/Desktop/hackeye/Videos/2d_1.mp4")
# vs = cv2.VideoCapture("/home/rangeesh/Desktop/hackeye/Videos/49.mp4")

fps = vs.get(cv2.CAP_PROP_FPS)
width  = vs.get(3)  # float
height = vs.get(4) # float

print('FPS is ' + str(fps))
print('Width is ' + str(width))
print('Height is ' + str(height))

input("Press 2: ")
# vs = cv2.VideoCapture("/home/rangeesh/Desktop/hackeye/Videos/49.mp4")
# vs = cv2.VideoCapture("http://192.168.0.14:8080")
# --------------------------------- Video END -------------------------------- #



# ------- If Livestream - Make sure to change ret,frame to frame alone ------- #
# vs = VideoStream(src=1).start()

# ---------------------------- Definition of Lists --------------------------- #
xlist = deque()
ylist = deque()
rlist = deque()
xlist_csv = []
ylist_csv = []
rlist_csv = []
tlist_csv = []
XWlist_csv = []
YWlist_csv = []
ZWlist_csv = []
framelist_csv=[]

# ---------------------------- To start the Webcam --------------------------- #
time.sleep(2.0)

# --------------- Initializing Variables for Exponential Filter -------------- #
flag = 0
exp_x=0
exp_y=0
exp_r=0

# ------ Exponential Filter Function - can be used only once ----------------- #
# -------------------- Not using it now, use it if needed -------------------- #
def exponential_filter(x,y,r):
    # Build Exponential Filter
    global flag, exp_x, exp_y, exp_r
    al = 0.1
    if flag == 0:
        exp_x=x
        exp_y=y
        exp_r=r
        flag =1
        return [x,y,r]
    
    ret_x = al*exp_x + (1-al)*x
    ret_y = al*exp_y + (1-al)*y
    ret_r = al*exp_r + (1-al)*r
    exp_x = ret_x
    exp_y = ret_y
    exp_r = ret_r
    return [ret_x,ret_y,ret_r]


# -------------------- Finding World Coordinates Function -------------------- #
def world_coordinates(u,v,r):

# ------------------------------ For video: 2d_1 ----------------------------- #
    f = 1017.036 # On average for close to or less than 40 inches Z
    X = (617-u)*RADIUS/r
    Y = (360-v)*RADIUS/r + 18*2.54 - f*RADIUS/(r*20)
    # You can have a function that calculates f - can be piece wise worst case
    Z = f*RADIUS/r
    return [X,Y,Z]



# -------------------------------- For General ------------------------------- #

    # X = u*RADIUS/r
    # Y = v*RADIUS/r
    # # You can have a function that calculates f - can be piece wise worst case
    # f = 1000 # On average for close to or less than 40 inches Z
    # Z = f*RADIUS/r
    # return [X,Y,Z]


# --- A better Update so that we can see the values change more peacefully --- #
ct = 0
# Update every UPDATE time instances, for example
x_disp = 0
y_disp = 0
radius_disp = 0
xw_disp = 0
yw_disp = 0
zw_disp = 0

# Frame Counter
ct_frames = 0

# ----------------------------------- Loop ----------------------------------- #
while True:

# ------------------------------ URL Stuff START ----------------------------- #
    # imgResp = urllib.urlopen(url)
    # imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
    # frame = cv2.imdecode(imgNp,-1)
# ------------------------------- URL Stuff END ------------------------------ #


# ------------------- Reading frame from video/live stream ------------------- #
    ct_frames = ct_frames+1
    print(ct_frames)
    ret, frame = vs.read() # Uncomment for Video
    # frame = vs.read() # Uncomment for Live Stream
    while frame is None:
        continue
    # print(frame)
    # print(type(frame))
    cv2.imshow("Frame", frame)
    # if not frame:
    #     frame = frame[1] if args.get("video",False) else frame
    if frame is None:
        break

# ---------------------------- CV Image Processing --------------------------- #
    # Resize, Blur, HSV
    frame = imutils.resize(frame,width=1800)
    blurred = cv2.GaussianBlur(frame,(11,11),0)
    hsv = cv2.cvtColor(blurred,cv2.COLOR_BGR2HSV)
    # Mask, Erosion, Dilation
    mask = cv2.inRange(hsv,greenLower,greenUpper)
    mask = cv2.erode(mask,None,iterations=2)
    mask = cv2.dilate(mask,None,iterations=2)
    # find contours in the mask and initialize the current
	# (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
	# only proceed if at least one contour was found
    if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid-.;
        c = max(cnts, key=cv2.contourArea)
        ((x_, y_), radius_) = cv2.minEnclosingCircle(c)

# ------------------------- Moving Average Filtering ------------------------- #
        if len(xlist) < MOVING_AVERAGE_WINDOW:
            xlist.append(x_)
            ylist.append(y_)
            rlist.append(radius_)
            continue

        xlist.popleft()
        xlist.append(x_)
        ylist.popleft()
        ylist.append(y_)
        rlist.popleft()
        rlist.append(radius_)
        x_mean = mean(xlist)
        y_mean = mean(ylist)
        radius_mean = mean(rlist)
        [XW,YW,ZW] = world_coordinates(x_mean,y_mean,radius_mean)

# ----------------------------- Appending to csv ----------------------------- #
        xlist_csv.append(x_mean)
        ylist_csv.append(y_mean)
        rlist_csv.append(radius_mean)
        XWlist_csv.append(XW)
        YWlist_csv.append(YW)
        ZWlist_csv.append(ZW)
        tlist_csv.append(time.time())
        framelist_csv.append(ct_frames)

        np.savetxt('CSV/xlist_csv.csv',xlist_csv,delimiter=',')
        np.savetxt('CSV/ylist_csv.csv',ylist_csv,delimiter=',')
        np.savetxt('CSV/rlist_csv.csv',rlist_csv,delimiter=',')
        np.savetxt('CSV/tlist_csv.csv',tlist_csv,delimiter=',')
        np.savetxt('CSV/XWlist_csv.csv',XWlist_csv,delimiter=',')
        np.savetxt('CSV/YWlist_csv.csv',YWlist_csv,delimiter=',')
        np.savetxt('CSV/ZWlist_csv.csv',ZWlist_csv,delimiter=',')
        np.savetxt('CSV/frame_list_csv.csv',framelist_csv,delimiter=',')



# ---------------------- Getting World Coordinates Frame --------------------- #

        # (x_w,y_w,radius_w) = world_coordinates(x,y,radius)

# ------------------------ Making a Clear Display Part ----------------------- #
        ct = ct+1

        if ct == UPDATE:
            x_disp = round(x_mean,1)
            y_disp = round(y_mean,1)
            radius_disp = round(radius_mean,1)
            xw_disp = XW
            yw_disp = YW
            zw_disp = ZW
            ct = 0

# -------------------------- Displaying on the Frame ------------------------- #
        S1 = ' Pixel Coordinates'
        S2 = ' Xc = ' + str(x_disp)
        S3 = ' Yc = ' + str(y_disp)
        S4 = ' Radius: ' + str(radius_disp)
        S5 = ' World Coordinates'
        S6 = ' X = ' + str(xw_disp)
        S7 = ' Y = ' + str(yw_disp)
        S8 = ' Z = ' + str(zw_disp)
        S9 = 'Frame Counter: ' + str(ct_frames) + ' Time: ' + str(ct_frames/25.0)

        cv2.putText(frame,S1,(40,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),1,cv2.LINE_AA)
        cv2.putText(frame,S2,(40,70),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,0),1,cv2.LINE_AA)
        cv2.putText(frame,S3,(40,100),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,0),1,cv2.LINE_AA)
        cv2.putText(frame,S4,(40,130),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,0),1,cv2.LINE_AA)
        cv2.putText(frame,S5,(40,170),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),1,cv2.LINE_AA)
        cv2.putText(frame,S6,(40,200),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,0),1,cv2.LINE_AA)
        cv2.putText(frame,S7,(40,230),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,0),1,cv2.LINE_AA)
        cv2.putText(frame,S8,(40,260),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,0),1,cv2.LINE_AA)
        cv2.putText(frame,S9,(40,290),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,0),1,cv2.LINE_AA)

# ----------------------- Drawing Circle and Trajectory ---------------------- #

        M = cv2.moments(c)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        # [x,y,radius] = exponential_filter(x,y,radius)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		# only proceed if the radius meets a minimum size
        if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
	# update the points queue
    pts.appendleft(center)

    	# loop over the set of tracked points
    for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
        if pts[i - 1] is None or pts[i] is None:
            continue
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
        thickness = int(np.sqrt(LEN / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
	# show the frame to our screen
    cv2.imshow("Frame", frame)

# -------------------------------- Time pause -------------------------------- #
    time.sleep(0.5)

    key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
# if we are not using a video file, stop the camera video stream

# -- Store in csv files, beware they get replaced - so save them separately -- #

print("Storing...")
# np.savetxt("~/test.csv", np.column_stack((xlist_csv,ylist_csv,rlist_csv)), delimiter=",", fmt='%s', header=['U','V','R'])
print("Stored")


if not args.get("video", False):
	vs.stop()
# otherwise, release the camera
else:
	vs.release()
# close all windows
cv2.destroyAllWindows()
