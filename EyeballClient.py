import socket as s
from struct import pack as p
import cv2
import numpy as np

def detect_eyes(img, cascade):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eyes = cascade.detectMultiScale(gray_frame, 1.3, 5) # detect eyes
    width = np.size(img, 1) # get face frame width
    height = np.size(img, 0) # get face frame height
    left_eye = None
    right_eye = None
    
    for (x, y, w, h) in eyes:
        if y > height / 2:
            pass
        eyecenter = x + w / 2  # get the eye center
        if eyecenter < width * 0.5:
            left_eye = img[y:y + h, x:x + w]
        else:
            right_eye = img[y:y + h, x:x + w]
    return left_eye, right_eye

def detect_faces(img, cascade):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = cascade.detectMultiScale(gray_frame, 1.3, 5)
    if len(coords) > 1:
        biggest = (0, 0, 0, 0)
        for i in coords:
            if i[3] > biggest[3]:
                biggest = i
        biggest = np.array([i], np.int32)
    elif len(coords) == 1:
        biggest = coords
    else:
        return None
    for (x, y, w, h) in biggest:
        frame = img[y:y + h, x:x + w]
    return frame

def cut_eyebrows(img):
    height, width = img.shape[:2]
    eyebrow_h = int(height / 4)
    img = img[eyebrow_h:height, 0:width]  # cut eyebrows out (15 px)return img
    return img

def blob_process(img, threshold, detector):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)
    img = cv2.erode(img, None, iterations=2) #1
    img = cv2.dilate(img, None, iterations=4) #2
    img = cv2.medianBlur(img, 5) #3
    keypoints = detector.detect(img)
    return keypoints

def detect_nose(img,cascade):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h,w = img.shape[:2]
    roi_gray = gray_frame[0:h, 0:w]
    roi_color = img[0:h, 0:h]
    nose = cascade.detectMultiScale(roi_gray)
    
    if len(nose) > 1:
        print("Too many noses detected. Selecting first...")
        #return nose[0]

    return nose

def nothing(x):
    pass

def main():
    f = open('p.txt', 'r')
    path = f.read()
    f.close()    



    face_cascade = cv2.CascadeClassifier(path + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(path + 'haarcascade_eye.xml')
    nose_cascade = cv2.CascadeClassifier(path + 'haarcascade_mcs_nose.xml')
    




    #img = cv2.imread("example.jpeg")
    detector_params = cv2.SimpleBlobDetector_Params()
    detector_params.filterByArea = True
    detector_params.maxArea = 1500
    detector = cv2.SimpleBlobDetector_create(detector_params)
    #gray_picture = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)#make picture gray
    #faces = face_cascade.detectMultiScale(gray_picture, 1.3, 5)

    cap = cv2.VideoCapture(0)
    cv2.namedWindow('image')
    cv2.createTrackbar('threshold', 'image', 0, 255, nothing)
    while True:
        _, frame = cap.read()
        face_frame = detect_faces(frame, face_cascade)
        if face_frame is not None:
            noses = detect_nose(frame, nose_cascade)
            
            for n in noses:
                cv2.rectangle(frame,(n[0],n[1]),(n[0]+n[2],n[1]+n[3]),(0,255,0),2)
            

            eyes = detect_eyes(face_frame, eye_cascade)
            for eye in eyes:
                if eye is not None:
                    threshold = cv2.getTrackbarPos('threshold', 'image')
                    eye = cut_eyebrows(eye)
                    keypoints = blob_process(eye, threshold, detector)
                    eye = cv2.drawKeypoints(eye, keypoints, eye, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow('image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
# read the path to the CV2 data

#cv2.drawKeypoints(eye, keypoints, eye, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

#for (x,y,w,h) in faces:
#    cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)
#    gray_face = gray_picture[y:y+h, x:x+w] # cut the gray face frame out
#    face = img[y:y+h, x:x+w] # cut the face frame out
#    eyes = eye_cascade.detectMultiScale(gray_face)
#    for (ex,ey,ew,eh) in eyes: 
#        cv2.rectangle(face,(ex,ey),(ex+ew,ey+eh),(0,225,255),2)
    

#cv2.imshow('my image',img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()



if __name__ == "__main__":
    main()



######## SOCKET STUFF ########
#sock = s.socket(s.AF_INET, s.SOCK_STREAM)
#sock.connect(("127.0.0.1", 42000))

#dat1 = p("hh", 65, 66)
#dat2 = p("hh", 67, 68)

#print(dat1)
#print(dat2)

#sock.send(dat1)
#sock.send(dat2)

#sock.close()
