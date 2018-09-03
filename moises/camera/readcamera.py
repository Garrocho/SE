import numpy as np
import cv2


def CaptureFrame():
    cap = cv2.VideoCapture(0)
    
    #Setting Camera Resolution
    cap.set(3, 640)
    cap.set(4, 480)
    
    # Capture frame
    for i in range(0,5):
        ret, frame = cap.read()
    
    frame = cv2.GaussianBlur(frame,(95,95),3)
    frame = frame[:,200:550]

    cv2.imwrite('Foto.png', frame)

    # When everything done, release the capture
    cap.release()

def FindTemplate():
    img_rgb = cv2.imread('Foto.png')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('template.png',0)
    w, h = template.shape[::-1]
    
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where( res >= threshold)
    #try:
    pt = zip(*loc[::-1])[0]
    # pt[0] eixo y, pt[1] eixo x 
    print 'X: ', pt[1], ' Y: ', pt[0]
    py = (392-pt[0])/14 - 4
    px = (343-pt[1])/14 + 9
    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
    #except:
    #py = 0
    #px = 5
    #print("Point: "+ str(px) + "," + str(py))
    cv2.imwrite('res.png',img_rgb)
    return [px,py]

CaptureFrame()
p = FindTemplate()
print (str(p[0]) + " " + str(p[1]) + " 0")
