from ROOT import TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TH2D, gStyle
import numpy as np
import time as t
import Scripts.header as h
import Scripts.reader as read
import Scripts.tasks as task

def plotTimeAlign(canvasName,boardId):

    eventStart = h.eventStart
    iupdate = h.updateIndex
    
    xBins = len(boardId)
    yBins = 80

    #initialize canvas and histograms
    hTimeAlign = TH2D(str(canvasName) + "TimeAlign",str(canvasName) + " TimeAlign",xBins,0,xBins,yBins,0,8)
    time_align = TCanvas(f"{canvasName}_time_align","time_align",800,400)
    hTimeAlign.GetXaxis().SetTitle("board")
    hTimeAlign.GetYaxis().SetTitle("timestamp")
    hTimeAlign.SetFillColor(38)
    gStyle.SetOptStat("ne")
    
    run = True
    i = eventStart
    iNext = len(h.iArr)
    h.iArr.append(i)


    while(run):
        i = h.iArr[iNext]
        if(i >= h.eventEnd):
            hTimeAlign.Draw("bar hist") 
            # add evt number
            hTimeAlign.SetTitle(f"{canvasName}_time_align: evt {i}")
            time_align.Modified()
            time_align.Update()
            # save on root file
            task.wrthisto(hTimeAlign, f"{canvasName}_Time_alignement")

            if i == 999999:
                print(f"{canvasName}_Time_alignement event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%iupdate == 0:
            print(f"{canvasName}_Time_alignement event number : {i}",flush=True)
            hTimeAlign.Draw("colz") 
            # add evt number
            hTimeAlign.SetTitle(f"{canvasName}_time_align: evt {i}")
            time_align.Modified()
            time_align.Update()
            # save on root file
            task.wrthisto(hTimeAlign, f"{canvasName}_Time_alignement")

        #initialize plot
        # if i == h.eventStart:
        #     for b in range(len(boardId)):  
        #         if type(boardId[b]) == str:
        #             hTimeAlign.Fill(f"{boardId[b]}",0)
        #         else:
        #             for d in range(len(boardId[b])):
        #                 hTimeAlign.Fill(f"{boardId[b][d]}",0)

        # wait for reader 
        while(h.iRead<=i):
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

        # load all hit boards 
        timeArr=np.double(h.myDir.timestamp)
        h.readingTree = False #----------------------------------------end flag

        #for each set of boards
        for b in range(0,len(boardId)):
            #if there's just one board:
            if type(boardId[b]) == int:
                bn = boardId[b] # I need just the number
               # count how many hits 
                for n in range(len(boardArr)):
                    if boardArr[n] == bn:
                        hTimeAlign.Fill(f"board_{boardId[b]}",timeArr[n],1)
            #if there are multiple boards:
            else:
                #for each board:
                for d in range(0,len(boardId[b])):
                    bn = boardId[b][d] # I need just the number
                    # count how many hits 
                    for n in range(len(boardArr)):
                        if boardArr[n] == bn:
                            hTimeAlign.Fill(f"board_{boardId[b][d]}",timeArr[n],1)


        h.iArr[iNext] += 1


