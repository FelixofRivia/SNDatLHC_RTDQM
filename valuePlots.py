from ROOT import TH1D, TCanvas,TFile, gDirectory, gSystem, gStyle
import numpy as np
import time as t
import header as h
import tasks as task
import math
import ROOT
import reader as read

def plotValueBoard(canvasName, boardId):
    eventEnd = h.eventEnd
    eventStart = h.eventStart
        
    #initialize canvas and histograms
    hValues = TH1D(f"{canvasName} Value",f"{canvasName} Value",300,0,300)
    cvalues = TCanvas(f"{canvasName}_value",f"{canvasName}_value",800,400)
    hValues.GetXaxis().SetTitle("value (a.u.)")
    hValues.SetFillColor(38)
    gStyle.SetOptStat("ne")
    
    run = True
    i = eventStart
    iupdate = h.updateIndex
    iNext = len(h.iArr)
    h.iArr.append(i)


    while(run):
        i = h.iArr[iNext]
        if(i >= eventEnd):
            hValues.Draw("bar hist")
            # add evt number
            hValues.SetTitle(f"{canvasName} Value: evt {i}")
            cvalues.Modified()
            cvalues.Update()
            # save on root file
            task.wrtcanvas(cvalues, f"{canvasName}_value.png")

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
        if i%iupdate == 0:
            print(f"{canvasName} event number : {i}",flush=True)
            hValues.Draw("bar hist")
            # add evt number
            hValues.SetTitle(f"{canvasName} Value: evt {i}") 
            cvalues.Modified()
            cvalues.Update()
            # save on root file
            task.wrtcanvas(cvalues, f"{canvasName}_value.png")

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

        # load all values 
        values=np.uint8(h.myDir.value)
        h.readingTree = False #----------------------------------------end flag

        #for each set of boards
        for b in range(0,len(boardId)):
            #if there's just one board:
            if type(boardId[b]) == str:
                bn = int(boardId[b].strip("board_")) # I need just the number
               # find values 
                for n in range(0,len(boardArr)):
                    if boardArr[n] == bn:
                        hValues.Fill(values[n])

            #if there are multiple boards:
            else:
                #for each board:
                for d in range(0,len(boardId[b])):
                    bn = int(boardId[b][d].strip("board_")) # I need just the number
                    # find values 
                    for n in range(0,len(boardArr)):
                        if boardArr[n] == bn:
                            hValues.Fill(values[n])

        h.iArr[iNext] += 1