import numpy as np
import cv2

#image = cv2.imread("cv_test.jpg")
#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#gray = cv2.GaussianBlur(gray, (3, 3), 0)
##cv2.imshow("Gray", gray)
#cv2.waitKey(0)

#edged = cv2.Canny(gray, 10, 100)
##cv2.imshow("Edged", edged)
##cv2.waitKey(0)
##cv2.imwrite("edgy.jpg",edged)
## construct and apply a closing kernel to 'close' gaps between 'white'
## pixels
#kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
#closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
##cv2.imshow("Closed", closed)
##cv2.waitKey(0)
##cv2.imwrite("closed.jpg",closed)
## find contours (i.e. the 'outlines') in the image and initialize the
## total number of books found
#( _, cnts, _) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#cv2.drawContours(image, cnts, -1, (0,255,0), 3)
#
##total = 0
##
###print(len(cnts))
### loop over the contours
##for c in cnts:
### approximate the contour
##	peri = cv2.arcLength(c, True)
##	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
##
### if the approximated contour has four points, then assume that the
### contour is a book -- a book is a rectangle and thus has four vertices
##	if len(approx) == 4:
##		cv2.drawContours(image, [approx], -1, (0, 255, 0), 4)
##		total += 1	
##
### display the output
##print("I found {0} books in that image".format(total))
#cv2.imshow("Output", image)
#cv2.waitKey(0)##

def thresh_callback(thresh):
    edges = cv2.Canny(blur,thresh,thresh*2)
    drawing = np.zeros(img.shape,np.uint8)     # Image to draw the contours
    _, contours, _ = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        color = np.random.randint(0,255,(3)).tolist()  # Select a random color
        cv2.drawContours(drawing,[cnt],0,color,2)
        #cv2.imshow('output',drawing)
    fname = "./images/gif/gif2/" + str(thresh) + '.jpg'
    cv2.imwrite(fname,drawing)
    #cv2.imshow('input',img)

img = cv2.imread('cv_test_2.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(11,11),0)

#cv2.namedWindow('input',cv2.WINDOW_AUTOSIZE)

thresh = 100
max_thresh = 255

#cv2.createTrackbar('canny thresh:','input',thresh,max_thresh,thresh_callback)

#thresh_callback(thresh)

#if cv2.waitKey(0) == 27:
#    cv2.destroyAllWindows()

for i in range(160):
	thresh_callback(i)