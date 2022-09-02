# -*- coding: utf-8 -*-

from ctypes import windll
import pyautogui as pg
import time
import threading
import cv2 as cv
import numpy as np
from PIL import ImageGrab
from PIL import Image
from functools import partial
# multi-threading
from concurrent.futures import ThreadPoolExecutor, as_completed


print("Tichu counter ")

CardList = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
Cards = []
Cards.append('1')

for Card in CardList:
    Cards.append(Card)
    Cards.append(Card)
    Cards.append(Card)
    Cards.append(Card)


Dog = "Dog"
Phoenix = "Phoenix"
Dragon = "Dragon"

Cards.append(Dog)
Cards.append(Phoenix)
Cards.append(Dragon)

SearchCardList = ['1','2','3','4','5','6','7','8','9','10','j','q','k','a', Dog, Phoenix, Dragon]

SearchArea_pg = (748, 1028, 1044, 156) # x,y,w,h
SearchArea_cv2 = (700,940,1870,1180) # x1, y1, x2, y2

exitFlag = False


def PrintCards():
    printStr = ""
    LastCard = ""
    if len(Cards) > 0:
        LastCard = Cards[0]
    for s in Cards:
        if s == LastCard:
            printStr += s
        else:
            printStr += '\n'
            printStr += s
        LastCard = s
        
    print(printStr)
def RemoveCard(a):
    print("RemoveCard: ", a)
    if len(a) == 0:
        return

    try:
        if a.isdigit():
            if (int(a) > 0) and int(a) <= 10:
                Cards.remove(a)
        elif a == 'j' or a == 'J' or a == 'q' or a == 'Q' or a == 'k' or a == 'K' or a == 'a' or a == 'A':
             Cards.remove(a.upper())
        elif a == 'd' or a == "Dog":
               Cards.remove(Dog)
        elif a == 'd' or a == "Dragon":
            Cards.remove(Dragon)
        elif a == 'p' or a == 'Phoenix':
            Cards.remove(Phoenix)
    except ValueError:
        pass
def PickupCards_pg(card):
    imgName = card + ".png"

    results = pg.locateAllOnScreen(imgName, confidence =0.8, grayscale = True, region=SearchArea_pg)
    results = list(results)

    filteredList = []
    if len(results) > 0:
        filteredList.append(results[0])

    for res in results:
        hasSameImg = False
        for i in filteredList:
            if (abs(res.left) - abs(i.left)) < 10 and (abs(res.top) - abs(i.top)) <  10:
                hasSameImg = True
                break
        if hasSameImg == True:
            continue

        filteredList.append(res)

    #for s in filteredList:
    #    print(s)
    #    pg.moveTo(s.left, s.top, 0.3)
    #    time.sleep(1)
   
    return len(filteredList)


def CaptureScreenImg():
    # 이 함수를 먼저 호출하는 것으로
    # 스크린 캡처를 검색보다 먼저 진행하기 때문에 1~dragon 카드를 검색하는 도중에 카드가 내어 지는 경우는 없다.
    # 카드를 내는 도중에 캡처하는 경우는 생길 수가 있겠지만.. 이것은 여러번 캡쳐해서 교차검증을 하면 

    # 사각형 영역 캡쳐해서 이미지화
    screenImg = ImageGrab.grab(bbox=SearchArea_cv2)
    screenImg = np.array(screenImg)
    screenImg = cv.cvtColor(screenImg, cv.COLOR_BGR2GRAY)
    return screenImg

def PickupCards_cv2(card, screenImg):

    templateName = card + ".png"

    ## 찾을 이미지
    template = cv.imread(templateName, cv.IMREAD_GRAYSCALE)

    h, w = template.shape

    method = cv.TM_CCOEFF_NORMED

    threshold = 0.85


    ## result(optional): 매칭 결과, (W - w + 1) x (H - h + 1) 크기의 2차원 배열 [여기서 W, H는 입력 이미지의 너비와 높이, w, h는 템플릿 이미지의 너비와 높이]
    res = cv.matchTemplate(screenImg, template, method)

    # 최소 값, 최대 값, 최소 지점, 최대 지점
    # 최소 포인터의 값을 이용하여 유사도가 가장 낮을 때를 알 수 있다.
    # 가장 밝거나 가장 어두운 지점이 매칭되는 지점이다.
    # 보면 좋을 링크 https://velog.io/@codren/%ED%85%9C%ED%94%8C%EB%A6%BF-%EB%A7%A4%EC%B9%AD

    cnt = 0
    max_val = 0
    while True:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if max_val < threshold:
            break
    
        # 적중하는 곳을 찾으면
        if max_val > threshold:
            ## https://iop8890.tistory.com/9 (Numpy(넘파이) ndarray 다차원 배열 문법 참조
            ## 일단 2차원 배열에서 적중된 곳(가장 정확도가 최댓값) 으로부터 이미지 사이즈 +- 만큼 0으로 채워서 다시 검출 안되게 하고
            res[max_loc[1]-h :max_loc[1]+h, max_loc[0]-w : max_loc[0]+w] = 0
            ## 적중한곳에다가 네모그리기
            #screenImg = cv.rectangle(screenImg,(max_loc[0],max_loc[1]), (max_loc[0]+w+1, max_loc[1]+h+1), (0,255,0) )
            cnt += 1
            
    
    #cv.imwrite('output.png', screenImg)
    return cnt


def DisplayCaptureImage():
    image = cv.imread('output.png')
    # show the image, provide window name first
    cv.imshow('image window', image)
    # add wait key. window waits until user presses a key
    cv.waitKey()
    # and finally destroy/close all open windows
    cv.destroyAllWindows()

################### 멀티스레드로 실행 코드 #######################
def CountCardForThread(card, screenImg):
    count = PickupCards_cv2(card, screenImg)
    return (card, count)

def CountCards_MultiThread():
    screenImg = CaptureScreenImg()
    values_for_each_image = []
    with ThreadPoolExecutor(20) as executor:
        results = {executor.submit(CountCardForThread, card, screenImg) for card in SearchCardList}
        for result in as_completed(results):
            values_for_each_image.append(result.result())
    return(values_for_each_image)

#################################################################



def RunCardCounter_pg():
    lastCombo = []
    while True:
        #start check time
        start = time.time()
        combo = []
    
        for card in SearchCardList:
            num = PickupCards_pg(card)
            for i in range (0, num):
                combo.append(card)
    
        #print("PickupCards elapsed time :", time.time() - start)

        if lastCombo != combo: 
            print("verified")
            for c in combo:
                RemoveCard(c)

            print("--------------------------------------")
            PrintCards()
    
        lastCombo = combo


def RunCardCounter_cv2():
    lastCombo = []
    comboQueue = []

    while True:
        #start check time
        start = time.time()
        combo = []
    
        screenImg = CaptureScreenImg()
        for card in SearchCardList:
            num = PickupCards_cv2(card, screenImg)
            for i in range (0, num):
                combo.append(card)
    
        #print("PickupCards elapsed time :", time.time() - start)

        comboQueue.append(combo)
        if len(comboQueue) > 3:
            comboQueue.pop(0)

        if len(comboQueue) == 3:
            if comboQueue[0] == comboQueue[1] == combo and combo != lastCombo:
                print("Verified!!")
                lastCombo = combo
                comboQueue.clear()
                for c in combo:
                    RemoveCard(c)
                print("--------------------------------------")
                PrintCards()


        if exitFlag == True:
            print("program is ended by user")
            break;

def RunCardCounter_cv2_MultiThread():
    lastCombo = []
    comboQueue = []
    while True:
        # start check time
        start = time.time()
        combo = []
        res = CountCards_MultiThread()

        for r in res:
            for i in range(0, r[1]):
                combo.append(r[0])
        combo.sort()
    
        #print("PickupCards elapsed time[Multi-threading]:", time.time() - start)
 
        comboQueue.append(combo)
        if len(comboQueue) > 3:
            comboQueue.pop(0)

        if len(comboQueue) == 3:
            if comboQueue[0] == comboQueue[1] == combo and combo != lastCombo:
                print("Verified!!")
                lastCombo = combo
                comboQueue.clear()
                for c in combo:
                    RemoveCard(c)
                print("--------------------------------------")
                PrintCards()


        if exitFlag == True:
            print("program is ended by user")
            break;
        


def get_input():
    global exitFlag
    while True:
        keystrk=input("write 'exit' to restart counter \n")
        # thread doesn't continue until key is pressed
        if keystrk == "exit":
            exitFlag=True
            print("restart command excuted! \n")
            

i=threading.Thread(target=get_input)
i.start()

time.sleep(1)

while True:

    print("waiting...3")
    time.sleep(1)
    print("waiting...2")
    time.sleep(1)
    print("waiting...1")
    time.sleep(1)

    RunCardCounter_cv2_MultiThread()
    exitFlag = False



#RunCardCounter_pg()
#RunCardCounter_cv2()



 