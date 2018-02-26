from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage import measure
from skimage.measure import regionprops
import cv2

def is_movement(roi, background_average):
    roi = cv2.GaussianBlur(roi, (21, 21), 0)

    img_delta = cv2.absdiff(roi, background_average)

    thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    image, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    l_contour_areas = []

    for c in contours:
        l_contour_areas.append(cv2.contourArea(c))

    print(max(l_contour_areas))
    if max(l_contour_areas) > 150000:
        retval = True

    else:
        retval = False

    background_average = (background_average*0.999 + roi*0.001).astype('uint8')

    return retval, background_average


def preprocess(img):
 
    
    #additional img processing steps
    #img = cv2.GaussianBlur(gray_car_image,(3,3),0)
    #laplacian = cv2.Laplacian(img,cv2.CV_64F)
    
    
    
    #generating a threshold value for binarization of img
    threshold_value = threshold_otsu(img)
    #print(threshold_value)
    #binarization of image
    binary_car_image = img > threshold_value
    
    return [binary_car_image, img]


def findNumberPlate(binImg):
    plate_objects_cordinates = []
    plate_like_objects = []

    #assuming prior knowledge about number plate dimensions
    plate_dimensions = (25, 50, 20, 70)#(0.08*binImg.shape[0], 0.2*binImg.shape[0], 0.15*binImg.shape[1], 0.4*binImg.shape[1])
    min_height, max_height, min_width, max_width = plate_dimensions
    
    
    #get connected Regions
    label_image = measure.label(binImg)
    
    #go through every region
    regions = regionprops(label_image)
    for region in regions:
        #throw away unlikely regions immediately
        if region.area < 50:
            #regions.remove(region)
            #if the region is so small then it's likely not a license plate
            continue

        # the bounding box coordinates
        min_row, min_col, max_row, max_col = region.bbox
        region_height = max_row - min_row
        region_width = max_col - min_col
        
        #region has to be inside the number plate dimensions
        if region_height >= min_height and region_height <= max_height and region_width >= min_width and region_width <= max_width and region_width > region_height:
            
            #ratio between height and width has to be inside a ceratin range
            if region_height/region_width < 0.9 and region_height/region_width > 0.2:
                plate_like_objects.append(binImg[min_row:max_row, min_col:max_col])
                plate_objects_cordinates.append((min_row, min_col, max_row, max_col))
            
    return plate_like_objects, plate_objects_cordinates