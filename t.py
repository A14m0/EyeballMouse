import cv2
import dlib
import socket as s
from struct import pack as p

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
    
def main():
    # prepare socket
    sock = connect_driver()
    
    # start video capture from 
    cap = cv2.VideoCapture(0)

    # define center point
    center_point = (0,0)

    while True:
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
            # send the point differences over the net to the driver
            send_diff(sock, x_df, y_df)

    # release the video capture and window handles 
    cap.release()    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()