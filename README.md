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
- 'Canny' algorithm is used to detect edges. It is an improvement on the sobel filter edge detection algorithm. 
- The sobel filter convolves a kernel that looks like the one below, over the image

![sobel filter image](/images/guide/SobelVertical.png)
![sobel filter image](/images/guide/SobelHorizontal.png)
- The first kernel selects  vertical edges, because it is symmetrical about horizontal axis.
- Similarly, the  second kernel selects horizontal edges
- Sobel filter otputs is not sharp and has a LOT of noise! This is solved by the canny algorithm
- Canny algorithm output is really sharp! This is achieved by a technique called non-max suppression.
- It also has very low noise. This is done by a clever type of thresholding.
- For understanding this in detail, theres a lot of great material! Check out [computerphile](https://youtu.be/sRFM5IEqR2w)!

## Line detection
- Line detection uses an algorithm called Hough transform
- For each point in an image, there are a lot of lines that can pass thorough that point. If we represent all these lines using some parameters, say slope and y-intercept, then the parameters of all lines that could pass through a point will form a line in the transform space.
- When the parmaters for possible lines for 2 points intersect at some point in the space of line parameters, Those line parameters will form the line that passes through the 2 points.
- For imperfect lines, those parameters will not intersect for all points, but at some location, they will all pass close. This will be detected as a  line.
- I know its hard to understand h=this completely from such shallow an explanation, please check out [some videos](https://youtu.be/6yVMpaIoxIU), they will make it easier to understand!

## Line filtering and grouping
- Now that we have our detected lines with us, we need to figure out the lane boundaries from them. First, lines that are too steep or too flat are removed.
- Then, lines with a positive slope are categorized as part of the right boundary and those with negative slope as that of left boundary
- Remeber that in images, the top-left corner is (0,0) and increases down and towards the right. This could be awkward, especially when talking about slope, for those of us used to normal cartesian space coordinates
- Now, the average of slope and intercept for these lines that we categorized before are computed, and these are taken as boundary ofthe lane!

Now, just take all that and do some math and overlay that on top of the original image! Thats it!
