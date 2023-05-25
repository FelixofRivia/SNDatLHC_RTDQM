from ROOT import TH1D, TCanvas,TFile, gDirectory, gSystem, gStyle
import numpy as np
import time as t
import header as h
import tasks as task
import math
import ROOT
import reader as read

hArrUSHitsPerCh = []
hArrDSHitsPerCh = []
hArrSciFiHitsPerCh = []
###################################################################################
########################## Plot Hits per Channel of a Detector ####################
###################################################################################
def plotHitsChDet(canvasName,boardId,boardName):

    #get number of boards to plot
    nCanv = 0
    if canvasName == 'SciFi':
        for arr in boardId:
            nCanv += len(arr)
    else:
        nCanv = len(boardId)

    #append global array with hists
    for n in range(1,nCanv+1):
        hist = TH1D(f"{canvasName}{n}_hits_per_channel",f"{canvasName}{n} hits per channel",512,0,512)
        hist.GetXaxis().SetTitle("channel ID")
        hist.GetYaxis().SetTitle("hits")
        hist.SetFillColor(38)
        eval(f"hArr{canvasName}HitsPerCh").append(hist)

    gStyle.SetOptStat("ne")

    #divide canvas
    hitsPerChannel = TCanvas(f"{canvasName}_hits_per_channel",f"{canvasName} hits per channel",600,800)
    x,y = 1,1
    if nCanv >= 3:
        x = 3
        y = math.ceil(nCanv/3)
    else:
        x = nCanv
    hitsPerChannel.Divide(x,y)


    run = True
    i = h.eventStart
    iNext = len(h.iArr)
    h.iArr.append(i)

    #looping through events:
    while(run):
        i = h.iArr[iNext]

        if(i >= h.eventEnd):
            #update histograms
            for n in range(1,nCanv+1):
                hitsPerChannel.cd(n)
                eval(f"hArr{canvasName}HitsPerCh")[n-1].Draw("bar hist")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            task.wrtcanvas(hitsPerChannel, f"{canvasName}_hits_per_channel.png")

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
            for n in range(1,nCanv+1):
                hitsPerChannel.cd(n)
                eval(f"hArr{canvasName}HitsPerCh")[n-1].Draw("bar hist")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            task.wrtcanvas(hitsPerChannel, f"{canvasName}_hits_per_channel.png")


        # wait for reader 
        waiting = True
        while(waiting):
            if (h.iRead>i):
                waiting=False
            else:
                t.sleep(5)

        #while sharing a value with rate or another thread
        read.avoidOverlap(i, iNext)

        while(h.readingTree):
            t.sleep(.005)

        h.readingTree = True #---------------------------------------------start flag
        entry = h.myDir.GetEntry(i)

        if entry <= 0:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue
        
        boardID = np.uint64(h.myDir.board_id)
        tofChannel = np.uint8(h.myDir.tofpet_channel)
        tofID = np.uint64(h.myDir.tofpet_id)
        h.readingTree = False #-------------------------------------------------end flag

       # check if array lenght is the same 
        if len(boardID) != len(tofChannel):
            print("ERROR: event ",i," len(boardID) != len(tofChannel)", flush=True)
            h.iArr[iNext] += 1
            continue

        if len(boardID) != len(tofID):
            print("ERROR: event ",i," len(boardID) != len(tofID)", flush=True)
            h.iArr[iNext] += 1
            continue

        if len(tofID) != len(tofChannel):
            print("ERROR: event ",i," len(tofID) != len(tofChannel)", flush=True)
            h.iArr[iNext] += 1
            continue

        #for each set of boards
        for b in range(0,len(boardId)):
            #if there's just one board:
            if type(boardId[b]) == str:
                for j, bn in enumerate(boardID):
                    if bn == int(boardId[b].strip("board_")):
                        ch = 64*tofID[j] + tofChannel[j]  
                        eval(f"hArr{canvasName}HitsPerCh")[b].Fill(ch,1)
                
            #if there are multiple boards:
            else:
                #for each board:
                for d in range(0,len(boardId[b])):
                    for j, bn in enumerate(boardID):
                        if bn == int(boardId[b][d].strip("board_")):
                            ch = 64*tofID[j] + tofChannel[j]  
                            eval(f"hArr{canvasName}HitsPerCh")[d+3*b].Fill(ch,1) #scifi is an array of arrays with 3 boards 

        h.iArr[iNext] += 1

###################################################################################
########################## Plot Hits per Channel of a Board #######################
###################################################################################
def plotHitsChannel(canvasName,boardNumber):
    
    hHitsPerChannel = TH1D(f"{canvasName}HitsPerChannel",f"{canvasName} Hits per channel",512,0,512)
    hHitsPerChannel.GetXaxis().SetTitle("channel ID")
    hHitsPerChannel.GetYaxis().SetTitle("hits")
    hHitsPerChannel.SetFillColor(38)
    hitsPerChannel = TCanvas(f"{canvasName}_hits_per_channel",f"{canvasName} hits per channel",600,800)
    gStyle.SetOptStat("ne")

    eventEnd = h.eventEnd
    eventStart = h.eventStart

    i = eventStart
    run = True
    iNext = len(h.iArr)
    h.iArr.append(i)
    #loop through all entries
    while(run):
        i = h.iArr[iNext]
        #update
        if i%h.updateIndex == 0:
            print(f"{canvasName} event number : {i}",flush=True)
            hHitsPerChannel.Draw("bar hist")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            task.wrtcanvas(hitsPerChannel, f"{canvasName}_hits_per_channel.png")

        if(i >= eventEnd):
            #update
            hHitsPerChannel.Draw("bar hist")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            task.wrtcanvas(hitsPerChannel, f"{canvasName}_hits_per_channel.png")

            if i == 999999:
                print(f"{canvasName} event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()
            
            
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

        h.readingTree = True #-------------------------------------------------start flag
        
        #load in value. If invalid (<= 0), discard
        bb = h.myDir.GetEntry(i)
        if bb <= 0:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue
        
        boardID = np.uint64(h.myDir.board_id)
        #Check if the selected board is hit
        if boardNumber not in boardID:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue

        tofChannel = np.uint8(h.myDir.tofpet_channel)
        tofID = np.uint64(h.myDir.tofpet_id)
        h.readingTree = False #-------------------------------------------------end flag

        # check if array lenght is the same 
        if len(boardID) != len(tofChannel):
            print("ERROR: event ",i," len(boardID) != len(tofChannel)", flush=True)
            h.iArr[iNext] += 1
            continue

        if len(boardID) != len(tofID):
            print("ERROR: event ",i," len(boardID) != len(tofID)", flush=True)
            h.iArr[iNext] += 1
            continue

        if len(tofID) != len(tofChannel):
            print("ERROR: event ",i," len(tofID) != len(tofChannel)", flush=True)
            h.iArr[iNext] += 1
            continue

        for j, bn in enumerate(boardID):
            if bn == boardNumber:
                ch = 64*tofID[j] + tofChannel[j]  
                hHitsPerChannel.Fill(ch,1)

        h.iArr[iNext] += 1

###################################################################################
########################## Plot Hits per Board ####################################
###################################################################################
def plotHitsBoard(canvasName, boardId, boardName):
    logy = False
    if canvasName == "total" or canvasName == "Total":
        logy = True

    eventEnd = h.eventEnd
    eventStart = h.eventStart
        
    #initialize canvas and histograms
    hHitsPerBoard = TH1D(f"{canvasName}HitsPerBoard",f"{canvasName} Hits per board",len(boardId),0,len(boardId))
    hits_per_board = TCanvas(f"{canvasName}_hits_per_board","hitsPerBoard",800,400)
    if logy:
        hHitsPerBoard.SetMinimum(.1)
    else:
        hHitsPerBoard.SetMinimum(0)
    hits_per_board.SetLogy(logy)
    hHitsPerBoard.GetXaxis().SetTitle("board")
    hHitsPerBoard.GetYaxis().SetTitle("hits")
    hHitsPerBoard.SetFillColor(38)
    gStyle.SetOptStat("ne")
    
    run = True
    i = eventStart
    iNext = len(h.iArr)
    h.iArr.append(i)


    while(run):
        i = h.iArr[iNext]
        if(i >= eventEnd):
            #update histograms
            max = hHitsPerBoard.GetBinContent(hHitsPerBoard.GetMaximumBin())
            #print(f" max = {max}",flush = True)
            if logy:
                hHitsPerBoard.SetMaximum(max*1.5)
            else:
                hHitsPerBoard.GetYaxis().SetRange(0,int(max*2))
            hHitsPerBoard.Draw("bar hist") 
            hits_per_board.Modified()
            hits_per_board.Update()
            # save on root file
            task.wrtcanvas(hits_per_board, f"{canvasName}_hits_per_board.png")

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
            max = hHitsPerBoard.GetBinContent(hHitsPerBoard.GetMaximumBin())
            #print(f" max = {max}",flush = True)
            if logy:
                hHitsPerBoard.SetMaximum(max*1.5)
            else:
                hHitsPerBoard.GetYaxis().SetRange(0,int(max*2))
            hHitsPerBoard.Draw("bar hist") 
            hits_per_board.Modified()
            hits_per_board.Update()
            # save on root file
            task.wrtcanvas(hits_per_board, f"{canvasName}_hits_per_board.png")

        #initialize plot
        if i == h.eventStart:
            for b in range(len(boardId)):
                if type(boardId[b]) == str:
                    hHitsPerBoard.Fill(f"{boardId[b]}",0)
                else:
                    for d in range(len(boardId[b])):
                        hHitsPerBoard.Fill(f"{boardId[b][d]}",0)

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

        # load all hit boards 
        boardArr=np.uint8(h.myDir.board_id)
        h.readingTree = False #----------------------------------------end flag

        #for each set of boards
        for b in range(0,len(boardId)):
            #if there's just one board:
            if type(boardId[b]) == str:
                bn = int(boardId[b].strip("board_")) # I need just the number
               # count how many hits 
                weight=0
                for bid in boardArr:
                    if bid == bn:
                        weight = weight +1

                hHitsPerBoard.Fill(boardId[b],weight)
            #if there are multiple boards:
            else:
                #for each board:
                for d in range(0,len(boardId[b])):
                    bn = int(boardId[b][d].strip("board_")) # I need just the number
                    # count how many hits 
                    weight=0
                    for bid in boardArr:
                        if bid == bn:
                            weight = weight +1

                    hHitsPerBoard.Fill(boardId[b][d],weight)

        h.iArr[iNext] += 1

