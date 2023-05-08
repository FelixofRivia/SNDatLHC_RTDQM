from pyexpat.errors import XML_ERROR_CANT_CHANGE_FEATURE_ONCE_PARSING
from ROOT import TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TH2D
import numpy as np
import array
import time as t
import header as h

def plot2DMap(xBoardNumber,yBoardNumber,xChannels,yChannels,canvasName,nCanvases,canvasIndex):
    #take in x, y board
    myVar = gDirectory.Get('event')

    xBoard = "board_" + str(xBoardNumber)
    xTree = gDirectory.Get(xBoard)
    yBoard = "board_" + str(yBoardNumber)
    yTree = gDirectory.Get(yBoard)
    eventEnd = h.eventEnd

    #grab their channels
    xBins = max(xChannels)
    yBins = max(yChannels)
    print("xMax = " + str(xBins))
    #make 2Dhist assigned with channels
    hitMap = TH2D(str(canvasName) + "HitsPerChannel" + str(canvasIndex),str(canvasName) + " nHits per channel",xBins,0,xBins,yBins,0,yBins)
    
    #make canvas with n divisions, cd to the index of the canvas
    xCanv = 1
    yCanv = 1
    if nCanvases > 3:
        xCanv = 3
        yCanv = nCanvases%xCanv
    canvas = TCanvas(canvasName + "_hits_per_channel",str(canvasName) + "HitsPerChannel",500*xCanv,500*yCanv)
    canvas.Divide(xCanv,yCanv)
    canvas.cd(canvasIndex)

    run = True
    i = 0
    #for each entry:
    while(run):

        if(i >= eventEnd):
            print(canvasName + str(canvasIndex) + " hits end = " + str(eventEnd))
            print(canvasName + str(canvasIndex) + " hits out of events, waiting...")
            t.sleep(h.refreshRate)
            h.reopenFile()
            t.sleep(3)
            myVar = gDirectory.Get('event')
            nEvents = myVar.GetEntriesFast()
            eventEnd = h.eventStart + nEvents
            print(canvasName + str(canvasIndex) + " hits eventEnd now = " + str(eventEnd))
        
       #load in value. If invalid (<= 0), discard
        if xTree.GetEntry(i) <= 0 or yTree.GetEntry(i) <= 0:
            i += 1
            continue

        if myVar.GetEntry(i) <= 0:
            i += 1
            continue
        
        xChArray = np.uint8(xTree.tofpet_channel)
        print("length = " + str(len(xChArray)))
        yChArray = np.uint8(yTree.tofpet_channel)

        xVal = -1
        yVal = -1
        #check x channels for a hit, save channel number
        #loop through defined channels
        j = 0
        for xch in xChArray:
            #grab the value in the channel
            if xch < 0:
                continue
            if xch in xChannels:
                #define wanted x channel
                xVal = xch
                #print("x = " + str(xVal))
                if yChArray[j] in yChannels:
                    yVal = yChArray[j]
                    #print("y = " + str(yVal))

            #plot hit point as x,y
            hitMap.Fill(xVal,yVal)
            j += 1
        #update

        if(i%h.updateIndex):
            hitMap.Draw("colz")
            canvas.Draw()
            canvas.Modified()
            canvas.Update()
            if (gSystem.ProcessEvents()):
                break

        i += 1

#array of x boards, array of y boards, a list of 
def plot2DMapSciFi(xBoardNumber,yBoardNumber,canvasName,nCanvases,canvasIndex):
    nChannels = 512*3   #ERROR: 1 daq board only 64 channels, check 512*3  

    #take in x, y board
    myVar = gDirectory.Get('event')

    x1Board = "board_" + str(xBoardNumber[0])
    x1Tree = gDirectory.Get(x1Board)
    y1Board = "board_" + str(yBoardNumber[0])
    y1Tree = gDirectory.Get(y1Board)
    x2Board = "board_" + str(xBoardNumber[1])
    x2Tree = gDirectory.Get(x2Board)
    y2Board = "board_" + str(yBoardNumber[1])
    y2Tree = gDirectory.Get(y2Board)
    x3Board = "board_" + str(xBoardNumber[2])
    x3Tree = gDirectory.Get(x3Board)
    y3Board = "board_" + str(yBoardNumber[2])
    y3Tree = gDirectory.Get(y3Board)
    eventEnd = h.eventEnd

    #grab their channels
    xBins = max(nChannels)
    yBins = max(nChannels)
    print("xMax = " + str(xBins))
    #make 2Dhist assigned with channels
    hitMap = TH2D(str(canvasName) + "HitsPerChannel" + str(canvasIndex),str(canvasName) + " nHits per channel",xBins,0,xBins,yBins,0,yBins)
    
    #make canvas with n divisions, cd to the index of the canvas
    xCanv = 1
    yCanv = 1
    if nCanvases > 3:
        xCanv = 3
        yCanv = nCanvases%xCanv
    canvas = TCanvas(canvasName + "_hits_per_channel",str(canvasName) + "HitsPerChannel",500*xCanv,500*yCanv)
    canvas.Divide(xCanv,yCanv)
    canvas.cd(canvasIndex)

    run = True
    i = 0
    #for each entry:
    while(run):

        if(i >= eventEnd):
            print(canvasName + str(canvasIndex) + " hits end = " + str(eventEnd))
            print(canvasName + str(canvasIndex) + " hits out of events, waiting...")
            t.sleep(h.refreshRate)
            h.reopenFile()
            t.sleep(3)
            myVar = gDirectory.Get('event')
            nEvents = myVar.GetEntriesFast()
            eventEnd = h.eventStart + nEvents
            print(canvasName + str(canvasIndex) + " hits eventEnd now = " + str(eventEnd))
        
       #load in value. If invalid (<= 0), discard
        if x1Tree.GetEntry(i) <= 0 and x2Tree.GetEntry(i) <= 0 and x3Tree.GetEntry(i) <= 0:
            i += 1
            continue

        if y1Tree.GetEntry(i) <= 0 and y2Tree.GetEntry(i) <= 0 and y3Tree.GetEntry(i) <= 0:
            i += 1
            continue

        if myVar.GetEntry(i) <= 0:
            i += 1
            continue
        
        xChArray = np.uint8(xTree.tofpet_channel)
        print("length = " + str(len(xChArray)))
        yChArray = np.uint8(yTree.tofpet_channel)

        xVal = -1
        yVal = -1
        #check x channels for a hit, save channel number
        #loop through defined channels
        j = 0
        for xch in xChArray:
            #grab the value in the channel
            if xch < 0:
                continue
            if xch in xChannels:
                #define wanted x channel
                xVal = xch
                #print("x = " + str(xVal))
                if yChArray[j] in yChannels:
                    yVal = yChArray[j]
                    #print("y = " + str(yVal))

            #plot hit point as x,y
            hitMap.Fill(xVal,yVal)
            j += 1
        #update

        if(i%h.updateIndex):
            hitMap.Draw("colz")
            canvas.Draw()
            canvas.Modified()
            canvas.Update()
            if (gSystem.ProcessEvents()):
                break

        i += 1