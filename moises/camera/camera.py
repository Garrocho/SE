import cv2
import numpy as np


def open_cap():
    cap = cv2.VideoCapture('http://haddad.local:6060/?action=stream')

    # Setting Camera Resolution
    cap.set(3, 640)
    cap.set(4, 480)

    return cap


def cap_frame(cap):
    # Capture frame
    for i in range(0, 20):
        ret, frame = cap.read()

    img = cv2.GaussianBlur(frame, (75, 75), 3)
    # img = frame[:, 230:610]
    img = frame[:, 230:550]
    img = cv2.bilateralFilter(img, 15, 75, 75)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # cv2.imwrite('Foto1.png', gray)

    return gray


def find_red_temp(gray):

    template = cv2.imread('tv.png')
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # run template matching, get minimum val
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    min_thresh = 0.75
    match_locations = np.where(res > min_thresh)

    # draw template match boxes
    w, h = template.shape[::-1]
    rets = []
    for (x, y) in zip(match_locations[1], match_locations[0]):
        ok = False
        if len(rets) == 0 and y < 280:
            rets.append((x, y))
        else:
            ok = False
            for i in rets:
                rx = abs(i[0] - x)
                ry = abs(i[1] - y)
                if rx > 15 and ry > 15 and y < 280:
                    ok = True
                else:
                    ok = False
            if ok:
                rets.append((x, y))
    if len(rets) > 0:
        return str(rets[0][0]) + ' ' + str(rets[0][1]) + ' 0'
    else:
        return '-1 -1 -1'


def find_black_temp(gray):

    template = cv2.imread('tp.png')
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # run template matching, get minimum val
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    min_thresh = 0.75
    match_locations = np.where(res > min_thresh)

    # draw template match boxes
    w, h = template.shape[::-1]
    rets = []
    for (x, y) in zip(match_locations[1], match_locations[0]):
        ok = False
        if len(rets) == 0 and y > 220:
            rets.append((x, y))
        else:
            ok = False
            for i in rets:
                rx = abs(i[0] - x)
                ry = abs(i[1] - y)
                if rx > 15 and ry > 15 and y > 220:
                    ok = True
                else:
                    ok = False
            if ok:
                rets.append((x, y))
    if len(rets) > 0:
        return str(rets[0][0]) + ' ' + str(rets[0][1]) + ' 0'
    else:
        return '-1 -1 -1'


def get_caps(cap):
    gray = cap_frame(cap)
    red = find_red_temp(gray)
    black = find_black_temp(gray)
    return red, black


cap = open_cap()

while True:
    red, black = get_caps(cap)
    file = open("caps.txt", "wb")
    file.write(red + '(8*8)' + black)
    file.close()
    print 'Get Caps...', red, black

cap.release()
