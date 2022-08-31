
from ctypes import windll
import pyautogui as pg
import time
import threading

from PIL import ImageGrab
from functools import partial

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
   

def PickupCards(card):
    imgName = card + ".png"

    results = pg.locateAllOnScreen(imgName, confidence =0.8, grayscale = True, region=(748, 1028, 1044, 156))
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



print("waiting...3")
time.sleep(1)
print("waiting...2")
time.sleep(1)
print("waiting...1")
time.sleep(1)

SearchCardList = ['1','2','3','4','5','6','7','8','9','10','j','q','k','a', Dog, Phoenix, Dragon]
lastCombo = []

while True:
    # start check time
    ##start = time.time()
    combo = []
    for card in SearchCardList:
        num = PickupCards(card)
        for i in range (0, num):
            combo.append(card)
    
    if lastCombo != combo: 
        print("verified")
        for c in combo:
            RemoveCard(c)
        print("--------------------------------------")
        PrintCards()
    
    lastCombo = combo

    ##print("PickupCards elapsed time :", time.time() - start)


 