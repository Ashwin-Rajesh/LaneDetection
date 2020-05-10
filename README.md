# Introduction
This project implements a simple lane detection system using Canny edge detect and Hough transform algorithms.

Implemented using OpenCV Python API

# Processing steps
1) Edge detection
2) Line detection
3) Detecting boundaries

## Overview
This system is quite simple. 
- First, the image feed is resized to a standard resolution, here, it is 1200 by 700.
- Image is converted to grayscale since the edge detection algorithm works in grayscale.
- Gaussian blur filter is applied to remove noise
- The canny edge detect algorithm is applied
- A mask is applied so that only relevant area is analysed
- Lines are deteted using Hough transform
- Lines are filtered, and grouped into left and right boundary, and boundary lines are detected

## Edge detection
- 'Canny' algorithm is used to detect edges. It is an improvement on the sobel filter. 
- The sobel filter convolves a kernel that looks like the one below, over the image

![sobel filter image](/images/guide/SobelVertical.png)
![sobel filter image](/images/guide/SobelHorizontal.png)
- The first kernel selects  vertical edges, because it is symmetrical about horizontal axis.
- Similarly, the  second kernel selects horizontal edges
- Sobel filter otputs is not sharp and has a LOT of noise! This is solved by the canny algorithm
- Canny algorithm output is really sharp! This is acchieved by a technique called non-max suppression.
- It also has very low noise. This is done by a clever type of thresholding.
- For understanding them in detail, theres a lot of great material! Check out computerphile!

## Line detection
- Line detection uses an algorithm called Hough transform
- The lines are 
