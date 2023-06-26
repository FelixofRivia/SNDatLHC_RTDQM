from ROOT import TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TH2D
import numpy as np
import time as t
import header as h
import reader as read
import tasks as task

def plot2DMap(xBoardNumber,yBoardNumber,xtofIDs,ytofIDs,canvasName,nCanvases,canvasIndex):

    xBoard = "board_" + str(xBoardNumber)
    yBoard = "board_" + str(yBoardNumber)

    eventStart = h.eventStart
    iupdate = h.updateIndex

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
        if(i >= h.eventEnd):
            hitMap.Draw("colz")
            canvas.Draw()
            # add evt number
            hitMap.SetTitle(str(canvasName) + f"HitsPerChannel: evt {i}")
            canvas.Modified()
            canvas.Update()
            # save on root file
            task.wrthisto(hitMap, f"{canvasName}_Hitmap")

            if i == 999999:
                print(f"{canvasName}_Hitmap event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%iupdate == 0:
            print(f"{canvasName}_Hitmap event number : {i}",flush=True)
            hitMap.Draw("colz")
            canvas.Draw()
            # add evt number
            hitMap.SetTitle(str(canvasName) + f"HitsPerChannel: evt {i}")
            canvas.Modified()
            canvas.Update()
            # save on root file
            task.wrthisto(hitMap, f"{canvasName}_Hitmap")
        # #initialize plot     to map bin with specific values
        # if i == h.eventStart:
        #     for b in range(len(boardId)):
        #         if type(boardId[b]) == str:
        #             hHitsPerBoard.Fill(f"{boardId[b]}",0)
        #         else:
        #             for d in range(len(boardId[b])):
        #                 hHitsPerBoard.Fill(f"{boardId[b][d]}",0)

        # wait for reader 
        while(h.iRead<=i):
            t.sleep(5)

        #while sharing a value with rate or another thread
        read.avoidOverlap(i,iNext)

        while(h.readingTree):
            t.sleep(.0005)
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
