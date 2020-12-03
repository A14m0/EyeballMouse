import cv2
import dlib
import socket as s
from struct import pack as p
from math import fabs

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("landmarks.dat")


def connect_driver():
    sock = s.socket(s.AF_INET, s.SOCK_STREAM)
    sock.connect(("127.0.0.1",42000))

    return sock

def send_diff(sock,x,y, lc=0,rc=0):
    # prepare flags integer
    click_flags = int((lc<<1)|(rc))
    # pack the data
    dat = p("hhh", x, y, click_flags)
    # send it
    sock.send(dat)
    
    
# notes for eye aspect ratio
#       (abs(p2-p6)+abs(p3-p5))
# EAR = -----------------------
#           2 * abs(p1-p4)
#
# where p1 is the left point, p4 is the right point
#       p2 is the upper left point (p6 lower left)
#       p3 is the upper right point (p5 lower right)
# source: https://www.pyimagesearch.com/2017/04/24/eye-blink-detection-opencv-python-dlib/
# for checks, just see when the ratio drops below about 0.1

# for our detector point map:
# p1 -> 36
# p2 -> 37
# p3 -> 38
# p4 -> 39
# p5 -> 40
# p6 -> 41

# helper function for absolute-ing points
def ap(p1, p2):
    val_x = p1.x - p2.x
    val_y = p1.y - p2.y
    
    distance = (val_x**2 + val_y**2)**0.5
    
    return distance
    
    
def get_aspects(lm):
    # get the ratios of each eye and return them
    ratio_left = (ap(lm.part(37),lm.part(41)) + ap(lm.part(38),lm.part(40)))/(2*ap(lm.part(36),lm.part(39))) 
    ratio_right = (ap(lm.part(43),lm.part(47)) + ap(lm.part(44),lm.part(46)))/(2*ap(lm.part(42),lm.part(45))) 
    
    # note we flip them here so the user's right eye is interpreted as a right-click, 
    # even thought the camera sees their right side on the left
    return (ratio_right, ratio_left)
    
    
def main():
    # prepare socket
    sock = connect_driver()
    
    # start video capture from 
    cap = cv2.VideoCapture(0)

    # define center point
    center_point = (0,0)

    while True:
        left_click = 0
        right_click = 0
        
        # capture a frame and prepare it
        _, frame = cap.read()
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        faces = detector(gray_img)

        for face in faces:
            # get face coordinate range to speed up landmark detection
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            # determine facial landmarks
            landmarks = predictor(gray_img, face)

            if center_point == (0,0):
                center_point = (landmarks.part(31).x,landmarks.part(31).y)
                print("New center point:", center_point) 
            
            # debug, show circles around landmarks
            """
            for n in range(0, 68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cv2.circle(frame, (x,y), 5, (0,255,0), 3)"""

            # show image
            #cv2.imshow(winname="Face", mat=frame)

            x_df = center_point[0]-landmarks.part(31).x
            y_df = landmarks.part(31).y-center_point[1]
            print("X difference:", x_df)
            print("Y difference:", y_df)
            
            # check to see if one or both eyes are blinking
            aspects = get_aspects(landmarks)
            
            if aspects[0] < 0.1:
                # left click
                left_click = 1
            if aspects[1] < 0.1:
                # right click
                right_click = 1
                
            # check if user blinked
            if right_click == 1 and left_click == 1:
                left_click = 0
                right_click = 0
            
            # send the point differences over the net to the driver
            send_diff(sock, x_df, y_df, left_click, right_click)

    # release the video capture and window handles 
    cap.release()    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
