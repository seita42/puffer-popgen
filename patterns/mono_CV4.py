from __future__ import division, print_function
import numpy as np
import cv2               # OpenCV 4.x
import sys, os
import math
import yaml
from collections import OrderedDict

##### YAML <-> OrderedDict
def represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())
def construct_odict(loader, node):
    return OrderedDict(loader.construct_pairs(node))
yaml.add_representer(OrderedDict, represent_odict)
yaml.add_constructor('tag:yaml.org,2002:map', construct_odict)
######

### default parameters
param = OrderedDict()
param['diameter'] = 20
param['sigmaColor'] = 150
param['sigmaSpace'] = 150
param['a_thresh_type'] = 0
param['a_thresh_blocksize'] = 10
param['a_thresh_offset'] = 0
param['a_thresh_offset2'] = 2
### 

initializing = True

###### input & output files
argv = sys.argv
infile = argv[1]
fname, ext = os.path.splitext(infile)

mono_file = fname + "_mono.bmp"
param_file = fname + "_param.yml"

###### global images & variants
disp_contours_mono = True

img_in = cv2.imread(infile, cv2.IMREAD_COLOR)

img_out_mono = np.zeros(img_in.shape[0:2], np.uint8)

if os.path.exists(param_file):             # load param file (if exists)
    with open(param_file, 'r') as f:
        param = yaml.safe_load(f)

# kernel = np.ones((7,7),np.uint8)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

def init():
    global initializing

    cv2.namedWindow("img_blur", cv2.WINDOW_NORMAL)

    cv2.createTrackbar("diameter", "img_blur", param['diameter'], 50, onSlidersChange)
    cv2.createTrackbar("sigmaColor", "img_blur", param['sigmaColor'], 300, onSlidersChange)
    cv2.createTrackbar("sigmaSpace", "img_blur", param['sigmaSpace'], 300, onSlidersChange)
    cv2.moveWindow("img_blur", 800, 200)

    
    cv2.namedWindow("param", cv2.WINDOW_NORMAL)

    cv2.createTrackbar("mean/Gauss", "param", param['a_thresh_type'], 1, onSlidersChange)
    cv2.createTrackbar("blocksize", "param", param['a_thresh_blocksize'], 100, onSlidersChange)
    cv2.createTrackbar("offset+", "param", param['a_thresh_offset'], 50, onSlidersChange)
    cv2.createTrackbar("offset-", "param", param['a_thresh_offset2'], 50, onSlidersChange)
    cv2.moveWindow("param", 800, 720)

    cv2.namedWindow("img_mono")
    cv2.moveWindow("img_mono", 1200, 720)

    initializing = False

def onSlidersChange(x):
    global initializing, param

    if initializing:
        print("[LOG]: Skipping onSlidersChange during initilization.")
        return
    
    param['diameter'] = cv2.getTrackbarPos("diameter", "img_blur")
    param['sigmaColor'] = cv2.getTrackbarPos("sigmaColor", "img_blur")
    param['sigmaSpace'] = cv2.getTrackbarPos("sigmaSpace", "img_blur")
    
    param['a_thresh_type'] = cv2.getTrackbarPos("mean/Gauss", "param")
    param['a_thresh_blocksize'] = cv2.getTrackbarPos("blocksize", "param")
    param['a_thresh_offset'] = cv2.getTrackbarPos("offset+", "param")
    param['a_thresh_offset2'] = cv2.getTrackbarPos("offset-", "param")

    processImage()
    
def processImage():
    global img_out_mono, img_out_cont, img_out_cont_r
    global stats
    
    ### blur image for easy-binarization
    img_blur = blur(img_in)
    cv2.imshow("img_blur", img_blur)
    # cv2.moveWindow("img_blur", 400, 100)

    ### make mono image
    img_blur_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
    img_mono = binarize(img_blur_gray)
    img_out_mono = img_mono
    cv2.imshow("img_mono", img_out_mono)
    # cv2.moveWindow("img_mono", 400, 600)

def blur(img):
    img_blur = cv2.bilateralFilter(img, param['diameter'], param['sigmaColor'], param['sigmaSpace'])
    
    return img_blur

def binarize(img):
    if param['a_thresh_type'] == 0:
        img_mono = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
                                         cv2.THRESH_BINARY, (param['a_thresh_blocksize'] + 1) * 2 + 1, \
                                         param['a_thresh_offset'] - param['a_thresh_offset2'])

    else:
        img_mono = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                         cv2.THRESH_BINARY, (param['a_thresh_blocksize'] + 1) * 2 + 1, \
                                         param['a_thresh_offset'] - param['a_thresh_offset2'])

    img_closing = cv2.morphologyEx(img_mono, cv2.MORPH_CLOSE, kernel)
    img_mono = img_closing

    img_opening = cv2.morphologyEx(img_mono, cv2.MORPH_OPEN, kernel)
    img_mono = img_opening
    
    return img_mono

#### main
init()
processImage()

while(1):
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Esc
        break

    elif key == ord('c'):  # toggle contours display (mono)
        disp_contours_mono = not disp_contours_mono
        processImage()

    elif key == ord('s'):  # save images, parameters
        print("save to: ", mono_file)
        cv2.imwrite(mono_file, img_out_mono)

        print("save to: ", param_file)
        with open(param_file, 'w') as f:
            f.write(yaml.dump(param, default_flow_style=False))
        print()

cv2.destroyAllWindows()
