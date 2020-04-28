# Object Tracking using Kalman Filters

> This is a project that is done as part of the course requiements for MEEN 689 - Robotic Perception. In brief, the project deals with identifying an object of a particular color in a contrasting background and extracting its coordinates and size in the camera frame. Upon applying a suitable version of the Kalman Filter, we track the object real time and with the measurements from object detection, estimate the position of the object in World Coordinates.


## Object Detection:
![](Gifs/Tracking.gif)
We are using the Hue/ HSV based OpenCV vision algorithm to detect the ball and determine it’s relative pixel position.  Utilizing contour detection algorithms, ball radius and center coordinate are determined.

The detection approach can be summarized as follows:

-  Frame-by-Frame images are obtained from the video captured

- The captured image is filtered using a Gaussian Blur filter to smoothen the image and filter out the noise.

- Based on color contrast/color identification, the ball is detected. This step required to tune the detection model using an iterative procedure of varying HSV range.

-  Create a mask of the image where the color is identified in the image (0-1) and remove white noise

-  Draw an enclosing circle around the object and get center coordinates and radius of the ball.

-  There can be many contours in the field of view.  The required contour will form a bigger contour compared to others because of the narrow color range.  Areas of the contours are calculated, and a threshold value is chosen pragmatically.  If the area of the contour is higher than the threshold, then we consider it else we ignore it.

-  Filter the data by obtaining the moving average

## Ways to capture data for object detection
> Due to the limitations in the equipment to capture images, we explored different ways to capture and calibrate from the sources we had

The following choices are enabled in the ball tracking code
- Object Detection taken from a video
- Real time Object detection using a Web Camera/ USB Camera
- Real Time Object detection using a Mobile Camera - images are fed using an IP camera from the smart phone


## Image Frame to World Frame Transformation:
Ball location and radius are obtained in the camera frame and are to be transformed into the world frame.

X_worldframe = X_imgframe * Radius/r_measured

Y_worldframe = Y_imgframe * Radius/r_measured

Z_worldframe = (focal length)*Radius/r_measured

The focal length of the camera was obtained experimentally, details in the next section.

## Calibration - Focal length determination:
Focal length was determined by measuring ball radius keeping it at various distances from the camera at an interval of 5 inches as shown below:

Focal Length, F = Z_worldframe * r_measured/ Actual_R

Least square estimate of Focal length, F = ∑ Z_worldframe/(∑ Actual_R/r_measured)


## UKF implementation
Filterpy package was used for UKF implementation. For the unscented transform, the sigma points were generated using method suggested by Van der Merwe et al using MerweScaledSigmaPoints in the Filterpy package. It was found to be the method discussed in the class. 

UKF.py is a Google colaboratory python notebook. The code is logically divided into cells making it easy to understand. The comments in the file are self explanatory. 
![](Gifs/UKF.gif)


## LSE implementation 
Given the data points over a time range and trying to fit them to the model of a projectile, it was decided to have a least squares fit to identify the initial velocities in both directions to be applied to the projectile model.

LSE.py has the needed equations and the closed form solution for finding the Velocities
![](Gifs/LSE.gif)
## Results

### LSE vs LSE
![](Gifs/LSE_vs_LSE_Part.gif)
### UKF vs LSE
![](Gifs/UKF_vs_LSE.gif)
### LSE vs UKF Part
![](Gifs/LSE_vs_UKF_Part.gif)


