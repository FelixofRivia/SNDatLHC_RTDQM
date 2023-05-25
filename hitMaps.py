from pyexpat.errors import XML_ERROR_CANT_CHANGE_FEATURE_ONCE_PARSING
from ROOT import TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TH2D
import numpy as np
import array
import time as t
import header as h
import reader as read
import tasks as task

def plot2DMap(xBoardNumber,yBoardNumber,xtofIDs,ytofIDs,canvasName,nCanvases,canvasIndex):

    xBoard = "board_" + str(xBoardNumber)
    yBoard = "board_" + str(yBoardNumber)

    eventStart = h.eventStart
    eventEnd = h.eventEnd

    #grab their channels
    xBins = 64*len(xtofIDs)#512 #64*8, but can be done better (select only needed channels, as in boardrate)
    yBins = 64*len(ytofIDs)
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
    i = eventStart

    iNext = len(h.iArr)
    h.iArr.append(i)


    while(run):
        i = h.iArr[iNext]
        if(i >= eventEnd):
            hitMap.Draw("colz")
            canvas.Draw()
            canvas.Modified()
            canvas.Update()
            # save on root file
            task.wrtcanvas(canvas, f"{canvasName}_2D_hitmap.png")

            if i == 999999:
                print(f"{canvasName} event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%h.updateIndex == 0:
            print(f"{canvasName} event number : {i}",flush=True)
            hitMap.Draw("colz")
            canvas.Draw()
            canvas.Modified()
            canvas.Update()
            # save on root file
            task.wrtcanvas(canvas, f"{canvasName}_2D_hitmap.png")
        # #initialize plot     to map bin with specific values
        # if i == h.eventStart:
        #     for b in range(len(boardId)):
        #         if type(boardId[b]) == str:
        #             hHitsPerBoard.Fill(f"{boardId[b]}",0)
        #         else:
        #             for d in range(len(boardId[b])):
        #                 hHitsPerBoard.Fill(f"{boardId[b][d]}",0)

        # wait for reader 
        waiting = True
        while(waiting):
            if (h.iRead>i):
                waiting=False
            else:
                t.sleep(5)

        #while sharing a value with rate or another thread
        read.avoidOverlap(i,iNext)

        while(h.readingTree):
            t.sleep(.005)
        h.readingTree = True #--------------------------------------------start flag

        # load in value. If invalid (<= 0), discard
        bb = h.myDir.GetEntry(i)
        if bb <= 0:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue

        nhits = h.myDir.n_hits
        if nhits <= 0:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue

        # load all hits 
        boardArr=np.uint8(h.myDir.board_id)
        tofChannel = np.uint8(h.myDir.tofpet_channel)
        tofID = np.uint8(h.myDir.tofpet_id)
        h.readingTree = False #----------------------------------------end flag

        xch=[]
        ych=[]
        # check if both boards are hit   real channels
        # if (xBoardNumber in boardArr) and (yBoardNumber in boardArr):
        #     for b in range(0,len(boardArr)):
        #         if xBoardNumber==boardArr[b] and tofID[b] in xtofIDs:
        #             xch.append(64*tofID[b] + tofChannel[b])
        #         if yBoardNumber==boardArr[b] and tofID[b] in ytofIDs:
        #             ych.append(64*tofID[b] + tofChannel[b])

        # check if both boards are hit  regrouped channels
        if (xBoardNumber in boardArr) and (yBoardNumber in boardArr):
            for b in range(0,len(boardArr)):
                if xBoardNumber==boardArr[b] and tofID[b] in xtofIDs:
                    try:
                        xch.append(64*xtofIDs.index(tofID[b]) + tofChannel[b])
                    except:
                        print("Ch not found in 2Dmaps...ignoring",flush=True)
                if yBoardNumber==boardArr[b] and tofID[b] in ytofIDs:
                    try:
                        ych.append(64*ytofIDs.index(tofID[b]) + tofChannel[b])
                    except:
                        print("Ch not found in 2Dmaps...ignoring",flush=True)
        # fill every combination
        if len(xch)>0 and len(ych)>0:
            for x in xch:
                for y in ych:
                    hitMap.Fill(x,y)

        h.iArr[iNext] += 1


#array of x boards, array of y boards, a list of 
# def plot2DMapSciFi(xBoardNumber,yBoardNumber,canvasName,nCanvases,canvasIndex):
#     nChannels = 512*3   #ERROR: 1 daq board only 64 channels, check 512*3  

#     #take in x, y board
#     myVar = gDirectory.Get('event')

#     x1Board = "board_" + str(xBoardNumber[0])
#     x1Tree = gDirectory.Get(x1Board)
#     y1Board = "board_" + str(yBoardNumber[0])
#     y1Tree = gDirectory.Get(y1Board)
#     x2Board = "board_" + str(xBoardNumber[1])
#     x2Tree = gDirectory.Get(x2Board)
#     y2Board = "board_" + str(yBoardNumber[1])
#     y2Tree = gDirectory.Get(y2Board)
#     x3Board = "board_" + str(xBoardNumber[2])
#     x3Tree = gDirectory.Get(x3Board)
#     y3Board = "board_" + str(yBoardNumber[2])
#     y3Tree = gDirectory.Get(y3Board)
#     eventEnd = h.eventEnd

#     #grab their channels
#     xBins = max(nChannels)
#     yBins = max(nChannels)
#     print("xMax = " + str(xBins))
#     #make 2Dhist assigned with channels
#     hitMap = TH2D(str(canvasName) + "HitsPerChannel" + str(canvasIndex),str(canvasName) + " nHits per channel",xBins,0,xBins,yBins,0,yBins)
    
#     #make canvas with n divisions, cd to the index of the canvas
#     xCanv = 1
#     yCanv = 1
#     if nCanvases > 3:
#         xCanv = 3
#         yCanv = nCanvases%xCanv
#     canvas = TCanvas(canvasName + "_hits_per_channel",str(canvasName) + "HitsPerChannel",500*xCanv,500*yCanv)
#     canvas.Divide(xCanv,yCanv)
#     canvas.cd(canvasIndex)

#     run = True
#     i = 0
#     #for each entry:
#     while(run):

#         if(i >= eventEnd):
#             print(canvasName + str(canvasIndex) + " hits end = " + str(eventEnd))
#             print(canvasName + str(canvasIndex) + " hits out of events, waiting...")
#             t.sleep(h.refreshRate)
#             h.reopenFile()
#             t.sleep(3)
#             myVar = gDirectory.Get('event')
#             nEvents = myVar.GetEntriesFast()
#             eventEnd = h.eventStart + nEvents
#             print(canvasName + str(canvasIndex) + " hits eventEnd now = " + str(eventEnd))
        
#        #load in value. If invalid (<= 0), discard
#         if x1Tree.GetEntry(i) <= 0 and x2Tree.GetEntry(i) <= 0 and x3Tree.GetEntry(i) <= 0:
#             i += 1
#             continue

#         if y1Tree.GetEntry(i) <= 0 and y2Tree.GetEntry(i) <= 0 and y3Tree.GetEntry(i) <= 0:
#             i += 1
#             continue

#         if myVar.GetEntry(i) <= 0:
#             i += 1
#             continue
        
#         xChArray = np.uint8(xTree.tofpet_channel)
#         print("length = " + str(len(xChArray)))
#         yChArray = np.uint8(yTree.tofpet_channel)

#         xVal = -1
#         yVal = -1
#         #check x channels for a hit, save channel number
#         #loop through defined channels
#         j = 0
#         for xch in xChArray:
#             #grab the value in the channel
#             if xch < 0:
#                 continue
#             if xch in xChannels:
#                 #define wanted x channel
#                 xVal = xch
#                 #print("x = " + str(xVal))
#                 if yChArray[j] in yChannels:
#                     yVal = yChArray[j]
#                     #print("y = " + str(yVal))

#             #plot hit point as x,y
#             hitMap.Fill(xVal,yVal)
#             j += 1
#         #update

#         if(i%h.updateIndex):
#             hitMap.Draw("colz")
#             canvas.Draw()
#             canvas.Modified()
#             canvas.Update()
#             if (gSystem.ProcessEvents()):
#                 break

#         i += 1