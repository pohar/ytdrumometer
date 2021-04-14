import cv2
import numpy as np
#from matplotlib import pyplot as plt
from PIL import ImageGrab as ig
#import time
#import sys
import pyautogui

pyautogui.PAUSE = 0
exresult = ''
eximage = np.zeros((128, 24, 3), np.uint8)
exsec = -1
result = 'XX_XXXX'
templates = []
window_image = np.ones((400,500,3),np.uint8)*127
seconds=-1
count=-1
count30 = 0
ticks, avgticks, excnt, avgticks = 0, 0, 0, 0

def newround():
    # TODO clear graph
    ticks, avgticks, excnt, avgticks = 0, 0, 0, 0
    count30 = 0
    yval = [0] * 60
    cv2.rectangle(window_image, (0, 140), (488, 400), (0, 127, 127), -1)
    cv2.line(window_image, (0, 400), (480, 140), (0, 0, 127))
    cv2.line(window_image, (240, 140), (240, 400), (0, 0, 127))

# Compare Two Images
def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


for i in range(10):
    actualchar = chr(48 + i)
    template_filename = 'digit' + actualchar + '.png'
    templates.append(cv2.imread(template_filename, 0))
    if templates[i] is None:
        print("Template file missing: " + template_filename)
        continue

xval = [i for i in range(60)]
yval = [0] * 60
newround()

loopcnt = 1
while loopcnt:
    #print("New loop")
    #match_start_time = time.time()
    screengrab = ig.grab(bbox=(368, 340, 368 + 132, 340 + 24))

    img_rgb = np.array(screengrab)  # this is the array obtained from conversion
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    #ret, img_gray = cv2.threshold(img_gray, 68, 255, cv2.THRESH_BINARY)
    backtorgb = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    #img_gray2 = np.array(backtorgb)
    roi = backtorgb[0:24, 0:128]
    window_image[40:40+24, 0:128] = roi

    # print("--- grab: %s seconds ---" % (time.time() - grab_start_time))
    result = 'XX_XXXX'

    #              0     1     2     3     4     5     6     7     8     9
    threshold = [0.80, 0.85, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80 ]
    if True:
        #for i in [1, 2, 3, 4, 5, 9, 8, 6, 7, 0]:  # order based on OCR
        for i in [1, 2, 3, 4, 5, 9, 8, 6, 7, 0 ]:  # order based on OCR
            actualchar = chr(48 + i)
            template = templates[i]

            if template is None:
                continue


            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED) #cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold[i])
            for pt in zip(*loc[::-1]):
                # cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 1)
                n = -1
                if pt[0] < 13:
                    n = 0
                elif pt[0] < 22:
                    n = 1
                elif pt[0] < 77:
                    n = 3
                elif pt[0] < 88:
                    n = 4
                elif pt[0] < 104:
                    n = 5
                elif pt[0] < 120:
                    n = 6

                #print("found (" + actualchar + ") at: ", pt[0], ":", pt[1], '->', n)
                if (n >= 0): # and (result[n] == 'X'):
                    result = result[0:n] + actualchar + result[n + 1:]  # digit index

        # display result
        #print(result)
        if result != exresult and result.count("X") == 0:
            #print(result)
            exresult = result
            seconds = int(result[0]) * 10 + int(result[1])
            count = int(result[3]) * 1000 + int(result[4]) * 100 + int(result[5]) * 10 + int(result[6])
            if seconds!=exsec:
                if(exsec==30) and (seconds == exsec-1):
                    if False:
                        pyautogui.leftClick(1070, 652)
                        pyautogui.typewrite(str(excnt))
                        pyautogui.hotkey('altright', 'v')
                        pyautogui.typewrite(str(exsec))
                        pyautogui.press('enter')
                    else:
                        print(excnt,'@',exsec)
                    count30 = excnt
                if (exsec != 60) and (seconds == 60):  # start new round
                    newround()

                ticks = count - excnt
                if seconds<60:
                    avgticks = count/(60-seconds)

                if (exsec == 1) and (seconds == 0):  # round over
                    print ("Result: ", count , '(', count30, '+', count-count30, ') avg:', round(avgticks,1))

                exsec = seconds
                excnt = count

                if seconds >= 60:
                    continue
                yval[seconds] = count

                p1 = ((60-seconds-1)*8, 400-int((400-140)*count/1200))
                p2 = ((60-seconds)*8, 400)
                cv2.rectangle(window_image, p1, p2, (127, 0, 0), -1)

        cv2.rectangle(window_image, (0, 65), (200, 120), (127,127,127), -1)
        cv2.putText(window_image, result, (0,75), cv2.FONT_HERSHEY_PLAIN, 1, 255)
        cv2.putText(window_image, str(seconds), (0,90), cv2.FONT_HERSHEY_PLAIN, 1, 255)
        cv2.putText(window_image, str(count), (30,90), cv2.FONT_HERSHEY_PLAIN, 1, 255)
        #stats
        cv2.putText(window_image, str(ticks), (90,90), cv2.FONT_HERSHEY_PLAIN, 1, 255)
        cv2.putText(window_image, str(round(avgticks,1)), (150,90), cv2.FONT_HERSHEY_PLAIN, 1, 255)

    cv2.imshow("Window", window_image)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    #loopcnt = loopcnt-1

cv2.destroyAllWindows()
print("End.")
