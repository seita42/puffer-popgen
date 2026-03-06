from __future__ import division, print_function

import numpy as np
import cv2
import os, sys

###### input & output files
argv = sys.argv
infile = argv[1]
savedir = argv[2]

fname, ext = os.path.splitext(os.path.basename(infile))

angle = 0
zoom = [0.125, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0]
zoomidx = 1   ### default 0.25

crop_x0, crop_y0, crop_x1, crop_y1 = -1, -1, -1, -1
drawing = False

def rotate_zoom_img(angle, zoomidx):
    global rows, cols, M
    global img_rot, img_s, img_s_view, img
    global zoom

    M = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
    img_rot = cv2.warpAffine(img_in, M, (cols, rows))
    img_s = cv2.resize(img_rot, None, fx=zoom[zoomidx], fy=zoom[zoomidx])
    img_s_view = img_s.copy()
    img = img_s_view.copy()
    cv2.imshow("img", img)
    
def draw_box(event, x, y, flags, param):
    global img_s, img_s_view, img
    global num
    global crop_x0, crop_y0, crop_x1, crop_y1
    global drawing
    global zoom, zoomidx
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if drawing == False:
            drawing = True
            crop_x0, crop_y0 = x, y
        else:
            drawing = False
            crop_x1, crop_y1 = x, y
            cv2.rectangle(img_s_view, (crop_x0, crop_y0), (crop_x1, crop_y1), (0, 0, 255), 2)
            img = img_s_view.copy()
            cv2.imshow("img", img)
            # crop_img = img_rot[crop_y0/zoom[zoomidx]:crop_y1/zoom[zoomidx], crop_x0/zoom[zoomidx]:crop_x1/zoom[zoomidx]]
            crop_img = img_s[crop_y0:crop_y1, crop_x0:crop_x1]
            save_crop(crop_img, num)
            num += 1

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img = img_s_view.copy()
            cv2.rectangle(img, (crop_x0, crop_y0), (x, y), (0, 255, 0), 2)
            cv2.imshow("img", img)

    elif event == cv2.EVENT_RBUTTONDOWN:
        drawing = False
        img = img_s_view.copy()
        cv2.imshow("img", img)


def save_crop(crop_img, n):
    global savedir, fname
    global angle, zoomidx, crop_x0, crop_y0, crop_x1, crop_y1
    
    outfile = savedir + "/" + fname + "_" + '{:02d}.jpg'.format(n)
    cv2.imwrite(outfile, crop_img)
    print(infile, outfile, angle, zoomidx, crop_x0, crop_y0, crop_x1, crop_y1)



#### main ####

# print("infile:", infile)
img_in = cv2.imread(infile, cv2.IMREAD_COLOR)
rows, cols = img_in.shape[:2]

rotate_zoom_img(angle, zoomidx)

num = 0

cv2.namedWindow('img')
cv2.setMouseCallback('img', draw_box)

while(1):
    key = cv2.waitKey(1) & 0xFF
    if key == 27: # Esc
        break

#    elif key == 2490368: # up
    elif key == ord('w'): # zoom in
        if zoomidx < (len(zoom) - 1):
            zoomidx += 1
        rotate_zoom_img(angle, zoomidx)

#    elif key == 2621440: # down
    elif key == ord('s'): # zoom out
        if zoomidx > 0:
            zoomidx -= 1
        rotate_zoom_img(angle, zoomidx)

#    elif key == 2424832: # left
    elif key == ord('a'): # rot left
        angle += 1
        rotate_zoom_img(angle, zoomidx)

#    elif key == 2555904: # right
    elif key == ord('d'): # rot right
        angle -= 1
        rotate_zoom_img(angle, zoomidx)

cv2.destroyAllWindows()

