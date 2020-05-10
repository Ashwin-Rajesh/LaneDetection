#!/home/ashwin/anaconda3/bin/python

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Detect edges - convert to grayscale, apply gaussian blur, apply canny algorithm
def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 1)
    ret  = cv2.Canny(gray, 50, 150)
    return ret

# Returns an image that has 255 for only required area, acting as a 'mask'. To apply it, the image is anded with the mask
def returnAoi(image):
    height  = image.shape[0]
    polygon = np.array([[(100,height),(250,500),(950,500),(1100,height)]])

    ret = np.zeros_like(image)
    cv2.fillPoly(ret, polygon, 255)
    return ret

# Returns an image that has all the lines passed
def displayLines(image, lines, colour = (255,0,0)):
    line_image = np.zeros_like(image)
    if(lines is not None):
        for line in lines:
            x1,y1,x2,y2 = line.astype(np.int)
            if((abs((y1-y2)/(x1-x2)) < 0.2) | (abs((y1-y2)/(x1-x2)) > 20)):
                continue
            cv2.line(line_image, (x1,y1), (x2, y2), colour, 10)
    return line_image

# Displays a mask of area between passed lane boundaries. Used for overlaying on original image
def displayLane(image, l_line, r_line, color = (255, 0, 0)):
    roi_image = np.zeros_like(image)
    if(l_line == (0,0,0,0)).all():
        return roi_image
    
    if(r_line == (0,0,0,0)).all():
        return roi_image
    
    polygon = np.zeros((1,4,2))
    
    polygon[0][0] = (l_line[0],l_line[1])
    polygon[0][1] = (l_line[2],l_line[3])
    polygon[0][2] = (r_line[2],r_line[3])
    polygon[0][3] = (r_line[0],r_line[1])


    polygon = polygon.astype(np.int)
    cv2.fillPoly(roi_image, polygon, color)
    return roi_image

# Returns the average of lines detected after splitting them as of left or right boundary based on their slope
def getAverageLines(image, lines) -> (np.ndarray, np.ndarray):
    left_lines = []
    right_lines = []

    for line in lines:
        x1, y1, x2, y2 = np.reshape(line,4)
        para = np.polyfit((x1,x2),(y1,y2),1)
        m = para[0]
        b = para[1]
        if((abs(m) < 0.2) | (abs(m) > 20)):
            continue
        if(m > 0):
            right_lines.append(para)
        else:
            left_lines.append(para)
    
    if (len(left_lines) == 0):
        left_lines.append((0,0))

    if (len(right_lines) == 0):
        right_lines.append((0,0))

    return (getCoords(image, np.average(left_lines, axis=0)), getCoords(image, np.average(right_lines, axis=0)))

# Returns the coordingates of line from slope and intercept form
def getCoords(image, para):
    if(para == (0,0)).all():
        return np.array((0,0,0,0))
    m = para[0]
    b = para[1]
    y1 = image.shape[0]
    y2 = 2 * y1 / 3
    x1 = (y1 - b) / m
    x2 = (y2 - b) / m
    if(x1 < 0):
        x1 = 0
        y1 = (m * x1) + b
    if(x2 < 0):
        x2 = 0
        y2 = (m * x2) + b
    
    if(x1 > 1200):
        x1 = 1200
        y1 = (m * x1) + b
    if(x2 > 1200):
        x2 = 1200
        y2 = (m * x2) + b
    return np.maximum(np.minimum(np.array((x1, y1, x2, y2)),10000 * np.ones(4)),-10000 * np.ones(4))

in_file_name = "youtube1.mp4"
out_file_name = os.path.splitext(in_file_name)[0] + "out3" + ".mp4"
vid_write = False

# Initialise video writer and video reader
if(vid_write):
    out = cv2.VideoWriter(out_file_name, cv2.VideoWriter_fourcc(*'XVID'), 24, (1200, 700))
video = cv2.VideoCapture(in_file_name)

# Ratio for calculating exponential moving average(EMA) - increasing this value increases smoothness, but increases delay
sum_ratio = 0.8
# Variables storing EMA for lane boundary lines
l_line_sum, r_line_sum = None, None

while(video.isOpened()):
    # Get image from capture
    _, image    = video.read()
    if image is None:
        break
    
    # Processing stages : Resize -> Edge detect(canny) -> Apply roi mask -> Detect lines(Hough)
    image = cv2.resize(image, (1200, 700))
    canny_image = canny(image)
    aoi         = returnAoi(canny_image)
    interest    = canny_image & aoi
    lines       = cv2.HoughLinesP(interest, 1, np.pi / 180, 100, minLineLength=20, maxLineGap=5) 
    
    # If no lines are detected, set right and left lines to (0,0,0,0)
    if lines is None:
        orig_lines_img = np.zeros_like(image)
        right_line = np.array((0,0,0,0))
        left_line  = right_line
    else:
        orig_lines_img = displayLines(image, lines.reshape((-1,4)))
        right_line, left_line = getAverageLines(image, lines)
    
    # If EMA is being calculated for first time, set as detected lines
    if(l_line_sum is None):
        l_line_sum = left_line
    if(r_line_sum is None):
        r_line_sum = right_line
    if (l_line_sum == (0,0,0,0)).all():
        l_line_sum = left_line
    if (r_line_sum == (0,0,0,0)).all():
        r_line_sum = right_line
    
    # Calculate next EMA
    if (left_line != (0,0,0,0)).any():
        l_line_sum = sum_ratio * l_line_sum + (1 - sum_ratio) * left_line
    if (right_line != (0,0,0,0)).any():
        r_line_sum = sum_ratio * r_line_sum + (1 - sum_ratio) * right_line
    
    # Make images for lines and roi, and blend them as required
    r_lines_img = displayLines(image, r_line_sum.reshape((1,4)), (255,0,0))
    l_lines_img = displayLines(image, l_line_sum.reshape((1,4)), (255,0,0))
    lines_img   = cv2.addWeighted(r_lines_img, 1, l_lines_img, 1, 1)
    roi_img     = displayLane(image, l_line_sum, r_line_sum, (0,255,0))
    blend_img   = cv2.addWeighted(roi_img, 0.7, image, 0.8, 1)
    blend_img   = cv2.addWeighted(lines_img, 1, blend_img, 0.8, 1)
    aoi_img = np.zeros_like(image)
    aoi_img[:,:,2] = aoi
    blend_img   = cv2.addWeighted(aoi_img , 0.5, blend_img, 1, 1)

    # Write the frame to video file
    if(vid_write):
        out.write(blend_img)

    # Display the frames and all lines detected
    cv2.imshow("frame", blend_img)
    cv2.imshow("all detected lines", orig_lines_img)

    if cv2.waitKey(1) == ord('q'):
        break

# Close all opened writers, readers and windows
if(vid_write):
    out.release()
video.release()
cv2.destroyAllWindows()
