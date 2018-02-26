from matplotlib import pyplot as plt
import numpy as np
import cv2
import Utils
import configparser

config = configparser.ConfigParser()
config.read('config/cams.ini')
stream_url = config['KurvenCam']['stream_url']
background_average = np.load("config/first_background_average.npy")

cap = cv2.VideoCapture(stream_url)
counter = 0
movement = False



while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    #convert to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #crop
    roi = gray[350:800, 500:1100]
    
    #before searching for number plates check if something interesting is in the picture
    movement, background_average = Utils.is_movement(roi, background_average)

    if movement:
        print(movement)
        binary_img = Utils.preprocess(roi,background_average)
        
        plate_like_objects, plate_objects_cordinates = Utils.findNumberPlate(binary_img[0])
        

        i = 0
        for coordinate in plate_objects_cordinates:

        	
            min_row, min_col, max_row, max_col = coordinate
            cv2.rectangle(roi,(min_col,min_row),(max_col,max_row),(255,0,0),3)

            #path = "outputpics/"+str(counter)+"_"+str(i)+".png"
            #cv2.imwrite(path, roi[min_row:max_row,min_col:max_col])
            #i=i+1
    

    # Display the resulting frame

    cv2.putText(roi, "Movement: {}".format(str(movement)), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow('frame',roi)
    
    counter = counter + 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
np.save("config/made_background_average.npy", background_average)