from ROOT import TH1D, TCanvas,TFile, gDirectory, gSystem, gStyle
import time as t
import ROOT
import header as h
import tasks as task
import numpy as np
import reader as read


###################################################################################
########################## Plot Global Rate #######################################
###################################################################################
def plotGlobalRate():
    #global plots are used by lumi function
    global hRate, hRateNorm

    #initialize variables

    t0 = h.t0
    run = True
    

    #set hists
    hRate = TH1D("hRate",f"Total Events per {h.rateBinwidth} sec",int(h.timeRange/h.rateBinwidth)+1,0,h.timeRange)
    hRateNorm = TH1D("hRateNorm","Events per second",int(h.timeRange/h.rateBinwidth)+1,0,h.timeRange)
    gStyle.SetOptStat("ne") #only plots hist name and n entries

    hRate.GetXaxis().SetTitle("time (sec)")
    hRate.GetYaxis().SetTitle("total events")
    hRateNorm.GetXaxis().SetTitle("time (sec)")
    hRateNorm.GetYaxis().SetTitle("events per second")
    hRate.SetMinimum(0)
    hRateNorm.SetMinimum(0)
    globalRate = TCanvas("globalRate","globalRate",600,800)
    globalRate.Divide(1,2)

    #initialize loop variables
    h.i = h.eventStart
    ts = 0
    retry = 0

    print(f"rate start = {h.eventStart}\trate end = {h.eventEnd}")

    while(run):

        #update
        if h.i%h.rateUpdate == 0:
            print(f"DQM event number : {h.i}",flush=True)
            #print(h.iArr,flush=True)
            globalRate.cd(1)
            hRate.Draw("hist")
            globalRate.cd(2)
            hRateNorm.Draw("e")
            globalRate.Modified()
            globalRate.Update()
            # save on root file
            task.wrtcanvas(globalRate, "globalRate.png")

        #if run out of events, wait and reopen file. Refresh final event
        if(h.i >= h.eventEnd):
            #update
            globalRate.cd(1)
            hRate.Draw("hist")
            globalRate.cd(2)
            hRateNorm.Draw("e")
            globalRate.Modified()
            globalRate.Update()
            # save on root file
            task.wrtcanvas(globalRate, "globalRate.png")
            #if end of file, print out and end thread
            if h.i == 999999:
                print("event = 999999. End of file.")
                h.i += 1  # otherwise other threads get stuck in the end 
                exit()
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()
        # wait for reader 
        waiting = True
        while(waiting):
            if (h.iRead>h.i):
                waiting=False
            else:
                t.sleep(5)
        #check to see if tree is being read. Put up flag while reading
        while(h.readingTree == True):
            t.sleep(.005)
        h.readingTree = True #------------------------------------------------------start flag

        #load in value. If invalid (<= 0), discard
        nb = h.myDir.GetEntry(h.i)
        if nb <= 0:
            h.i += 1
            h.readingTree = False
            continue

        #grab value and copy locally
        ts = h.myDir.evt_timestamp
        h.readingTree = False #------------------------------------------------------end flag
        time = (ts - t0)

        #if bad event, print out and try again
        if time < 0:
            print("---------------------------------------------------------bad")
            print(f"i =\t{h.i};\ttime =\t{time};\ttime = {time/h.tsPerSec} sec")
            print(f"t0 =\t{t0};\t{t0/h.tsPerSec} sec")
            print(f"ts =\t{ts};\t{ts/h.tsPerSec}")

            #if tried 3 times, skip index and keep going
            if retry >= 2:
                print(f"rate grabbed a bad value. Tried three times. Skipping...")
                h.i += 1
                retry = 0
                t.sleep(.25)
            else:
                print(f"rate grabbed a bad value. Retrying...")
                retry += 1
                t.sleep(.25)
            continue
        
        #reset hist at the end of the range
        if time/h.tsPerSec >= h.timeRange:
            # avoid random big numbers (better fix to do) 
            if (ts-t0)/h.tsPerSec >= 2*h.timeRange:
                print(f"Rate was about to set t0 = {ts/h.tsPerSec} s from {t0/h.tsPerSec} s",flush=True)
                continue
            #reset relative t0
            t0 = ts
            hRate.Reset()
            hRateNorm.Reset()

        #normalized rate
        hRateNorm.Fill(time/h.tsPerSec,1/h.rateBinwidth)
        #unnormalized rate
        hRate.Fill(time/h.tsPerSec,1)

        h.i += 1

###################################################################################
########################## Plot Rate of a Board ###################################
###################################################################################
def plotBoardRate(canvasName,boardNumber):
    board = "board_" + str(boardNumber)
    
    t0 = h.t0
    run = True
    stuck = 0

    #set hists
    hBoardRate = TH1D(f"{canvasName}Rate",f"{canvasName} Events per {h.rateBinwidth} sec",int(h.timeRange/h.rateBinwidth),0,h.timeRange)
    hBoardRateNorm = TH1D(f"{canvasName}RateNorm",f"{canvasName} Events per second",int(h.timeRange/h.rateBinwidth),0,h.timeRange)
    hBoardRate.GetXaxis().SetTitle("time (sec)")
    hBoardRate.GetYaxis().SetTitle("total events")
    hBoardRateNorm.GetXaxis().SetTitle("time (sec)")
    hBoardRateNorm.GetYaxis().SetTitle("events per second")
    hBoardRate.SetMinimum(0)
    hBoardRateNorm.SetMinimum(0)
    gStyle.SetOptStat("ne") #only plots hist name and n entries

    boardRate = TCanvas(f"{canvasName}Rate",canvasName,600,800)
    boardRate.Divide(1,2)
    
    i = h.eventStart
    #append index i to global array to avoid memory issues
    iNext = len(h.iArr)
    h.iArr.append(i)

    while(run):

        i = h.iArr[iNext]

        # if i%50000==0:
        #     print("board event " + str(i))

        #update
        if i%h.updateIndex == 0:
            print(f"{canvasName} event number : {i}",flush=True)
            boardRate.cd(1)
            hBoardRate.Draw("hist")
            boardRate.cd(2)
            hBoardRateNorm.Draw("e")
            boardRate.Modified()
            boardRate.Update()
            # save on root file
            task.wrtcanvas(boardRate, f"{canvasName}Rate.png")

        #if end of events in file
        if(i >= h.eventEnd):
            boardRate.cd(1)
            hBoardRate.Draw("hist")
            boardRate.cd(2)
            hBoardRateNorm.Draw("e")
            boardRate.Modified()
            boardRate.Update()
            # save on root file
            task.wrtcanvas(boardRate, f"{canvasName}Rate.png")

            #if end of file, exit
            if i == 999999:
                print("event = 999999. End of file.")
                exit()
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
       # do not overlap with other threads 
        read.avoidOverlap(i,iNext)

        while(h.readingTree):
            #print("waiting for tree...",flush = True)
            t.sleep(.005)
        h.readingTree = True #------------------------------------------start flag
        entry = h.myDir.GetEntry(i)
        ts = h.myDir.evt_timestamp
        n_hits = h.myDir.n_hits
        boardArr = np.uint8(h.myDir.board_id)
        h.readingTree = False #------------------------------------------end flag
        #load in value. If invalid (<= 0), discard       

        if n_hits <= 0:
            h.iArr[iNext] += 1
            continue
        
        #Check if the selected board is hit
        if boardNumber not in boardArr:
            h.iArr[iNext] += 1
            continue

        #keep time in original units until filling hist
        h.iArr[iNext] += 1

        #catch bad events
        time = ts-t0
        if time < 0:
            print("---------------------------------------------------------bad")
            print(f"i =\t{i};\ttime =\t{time};\ttime = {time/h.tsPerSec} sec",flush=True)
            print(f"t0 =\t{t0};\t{t0/h.tsPerSec} sec",flush=True)
            print(f"ts =\t{ts};\t{ts/h.tsPerSec}",flush=True)
            print(f"{canvasName} grabbed a bad value. Skipping...",flush=True)
            continue
        
        #count how many hits for the board  
        weight=0
        for bid in boardArr:
            if bid == boardNumber:
                weight = weight +1
                
        #normalized rate
        hBoardRateNorm.Fill((ts-t0)/h.tsPerSec,weight/h.rateBinwidth)
        #unnormalized rate
        hBoardRate.Fill((ts-t0)/h.tsPerSec,weight)

        #reset hist if past time range
        if (ts-t0)/h.tsPerSec >= h.timeRange:
           # avoid random big numbers (better fix to do) 
            if (ts-t0)/h.tsPerSec >= 2*h.timeRange:
                print(f"{canvasName} was about to set t0 = {ts/h.tsPerSec} s from {t0/h.tsPerSec} s",flush=True)
                continue
            t0 = ts
            hBoardRate.Reset()
            hBoardRateNorm.Reset()
           # print(f"{canvasName} set t0 = {t0/h.tsPerSec} s",flush=True)
            
