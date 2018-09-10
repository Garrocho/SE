import cv2
import numpy as np

AR = [350, 265] # area vermelha
AB = [350, 480] # area preta

def cap_frame():
    cap = cv2.VideoCapture(0)
    
    #Setting Camera Resolution
    cap.set(3, 640)
    cap.set(4, 480)
    
    # Capture frame
    for i in range(0,20):
        ret, frame = cap.read()
    
    img = cv2.GaussianBlur(frame,(75,75),3)
    img = frame[:,200:550]
    img = cv2.bilateralFilter(img,15,75,75)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cap.release()
    
    return gray
    
def find_red_temp(gray):

    template = cv2.imread('tv.png')
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # run template matching, get minimum val
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    min_thresh = 0.75
    match_locations = np.where(res>min_thresh)
    
    # draw template match boxes
    w, h = template.shape[::-1]
    rets = []
    for (x, y) in zip(match_locations[1], match_locations[0]):
        ok = False
        if len(rets) == 0:
            rets.append((x,y))
        else:
            ok = False
            for i in rets:
                rx = abs(i[0]-x)
                ry = abs(i[1]-y)
                if rx > 15 and ry > 15:
                    ok = True
                else:
                    ok = False
            if ok:
                rets.append((x,y))
    return rets
                
def find_black_temp(gray):
    
    template = cv2.imread('tp.png')
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # run template matching, get minimum val
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    min_thresh = 0.75
    match_locations = np.where(res>min_thresh)
    
    # draw template match boxes
    w, h = template.shape[::-1]
    rets = []
    for (x, y) in zip(match_locations[1], match_locations[0]):
        ok = False
        if len(rets) == 0:
            rets.append((x,y))
        else:
            ok = False
            for i in rets:
                rx = abs(i[0]-x)
                ry = abs(i[1]-y)
                if rx > 15 and ry > 15:
                    ok = True
                else:
                    ok = False
            if ok:
                rets.append((x,y))
    return rets

def get_caps(area):
    gray = cap_frame()
    vetor = []
    vetor.append({"red": find_red_temp(gray)})
    vetor.append({"black": find_black_temp(gray)})
    if area == 0:
        for p in vetor["black"]:
            if p[0] <= AR[0] and p[1] <= AR[1] and p[1] > AB[1]:
                return p
        for p in vetor["red"]:
            if p[0] <= AR[0] and p[1] <= AR[1] and p[1] > AB[1] and p[1] > 60:
                return p
    else:
        for p in vetor["red"]:
            if p[0] <= AB[0] and p[1] <= AB[1] and p[1] > AR[1]:
                return p
        for p in vetor["black"]:
            if p[0] <= AB[0] and p[1] <= (AB[1]-60) and p[1] > AR[1]:
                return p
    return None