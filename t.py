import cv2
import dlib

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("landmarks.dat")


cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = detector(gray_img)
    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        landmarks = predictor(gray_img, face)
        for n in range(0, 68):

            x = landmarks.part(n).x
            y = landmarks.part(n).y

            cv2.circle(frame, (x,y), 5, (0,255,0), 3)

    cv2.imshow(winname="Face", mat=frame)
    if cv2.waitKey(delay=0) == 27:
        break
    

cap.release()    
cv2.destroyAllWindows()







