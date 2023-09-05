from ROOT import TH1D, TCanvas,TFile, gDirectory, gSystem, gStyle, TH1
import time as t
import ROOT
import Scripts.header as h
import Scripts.tasks as task
import numpy as np
import Scripts.reader as read


###################################################################################
########################## Plot Global Rate #######################################
###################################################################################
def plotGlobalEvtRate():
    startT = t.perf_counter()
    #initialize variables
    t0 = h.t0
    run = True

    binwidth = h.rateBinwidth
    tps = h.tsPerSec
    iupdate = h.rateUpdate
    
    TH1.AddDirectory(False)
    #set hists
    hRate = TH1D("hRate",f"Total Events per {binwidth} s",int(h.timeRange/binwidth)+1,0,h.timeRange)
    hRateNorm = TH1D("hRateNorm","Events per second",int(h.timeRange/binwidth)+1,0,h.timeRange)
    gStyle.SetOptStat("ne") #only plots hist name and n entries

    hRate.SetDirectory(ROOT.nullptr)
    hRateNorm.SetDirectory(ROOT.nullptr)

    hRate.GetXaxis().SetTitle("time (s)")
    hRate.GetYaxis().SetTitle(f"events per {binwidth} s")
    hRateNorm.GetXaxis().SetTitle("time (s)")
    hRateNorm.GetYaxis().SetTitle("events per second")
    hRate.SetMinimum(0)
    hRateNorm.SetMinimum(0)
    globalRate = TCanvas("globalRate","globalRate",600,800)
    globalRate.Divide(1,2)

    #initialize loop variables
    h.i = h.eventStart
    ts = 0
    retry = 0

    while(run):
        i = h.i
        #update
        if i%iupdate == 0:
            print(f"TOT_Rate event number : {i}, Timer = {t.perf_counter()-startT}",flush=True)
            #print(h.iArr,flush=True)
            globalRate.cd(1)
            hRate.Draw("hist")
            globalRate.cd(2)
            hRateNorm.Draw("e")
            # add evt number
            hRate.SetTitle(f"Total Rate: evt {i}")
            hRateNorm.SetTitle(f"Total RateNorm: evt {i}")
            globalRate.Modified()
            globalRate.Update()
            # save on root file
            task.wrthisto(hRate, "TOT_Rate")
            task.wrthisto(hRateNorm, "TOT_Rate_norm")

        #if run out of events, wait and reopen file. Refresh final event
        if(i >= h.eventEnd):
            #update
            globalRate.cd(1)
            hRate.Draw("hist")
            globalRate.cd(2)
            hRateNorm.Draw("hist")
            # add evt number
            hRate.SetTitle(f"Total Rate: evt {i}")
            hRateNorm.SetTitle(f"Total RateNorm: evt {i}")
            globalRate.Modified()
            globalRate.Update()
            # save on root file
            task.wrthisto(hRate, "TOT_Rate")
            task.wrthisto(hRateNorm, "TOT_Rate_norm")
            #if end of file, print out and end thread
            if i == 999999:
                print(f"TOT_Rate event number = 999999. End of file. Timer = {t.perf_counter()-startT}", flush=True) 
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.i
                #refresh graph?  if not, do not reset t0
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()
        # wait for reader 
        while(h.iRead<=i):
            t.sleep(5)
        
        #check to see if tree is being read. Put up flag while reading
        while(h.readingTree == True):
            t.sleep(0)
        h.readingTree = True #------------------------------------------------------start flag
        #h.lock.acquire()
        #load in value. If invalid (<= 0), discard
        nb = h.myDir.GetEntry(i)
        if nb <= 0:
            h.i += 1
            h.readingTree = False
            continue

        #grab value and copy locally
        ts = h.myDir.evt_timestamp
        #h.lock.release()
        h.readingTree = False #------------------------------------------------------end flag
        time = (ts - t0)

        #if bad event, print out and try again
        if time < 0:
            print("---------------------------------------------------------bad")
            print(f"i =\t{i};\ttime =\t{time};\ttime = {time/tps} s")
            print(f"t0 =\t{t0};\t{t0/tps} s")
            print(f"ts =\t{ts};\t{ts/tps}")

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
        if time/tps >= h.timeRange:
            # avoid random big numbers (better fix to do) 
            if (ts-t0)/tps >= 2*h.timeRange:
                print(f"Rate was about to set t0 = {ts/tps} s from {t0/tps} s",flush=True)
                continue
            #reset relative t0
            t0 = ts
            hRate.Reset()
            hRateNorm.Reset()

        #normalized rate
        hRateNorm.Fill(time/tps,1/binwidth)
        #unnormalized rate
        hRate.Fill(time/tps,1)

        h.i += 1

###################################################################################
########################## Plot Rate of a Board ###################################
###################################################################################
def plotBoardHitRate(canvasName,boardNumber):
    board = "board_" + str(boardNumber)
    startT = t.perf_counter()
    t0 = h.t0
    run = True
    stuck = 0
    tps = h.tsPerSec
    binwidth = h.rateBinwidth
    iupdate = h.updateIndex

    #set hists
    hBoardRate = TH1D(f"{canvasName}Rate",f"{canvasName} Hits per {binwidth} s",int(h.timeRange/binwidth),0,h.timeRange)
    hBoardRateNorm = TH1D(f"{canvasName}RateNorm",f"{canvasName} Hits per second",int(h.timeRange/binwidth),0,h.timeRange)
    hBoardRate.GetXaxis().SetTitle("time (s)")
    hBoardRate.GetYaxis().SetTitle(f"hits per {binwidth} s")
    hBoardRateNorm.GetXaxis().SetTitle("time (s)")
    hBoardRateNorm.GetYaxis().SetTitle("hits per second")
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

        #update
        if i%iupdate == 0:
            print(f"{canvasName}_Rate event number : {i}, , Timer = {t.perf_counter()-startT}",flush=True)
            boardRate.cd(1)
            hBoardRate.Draw("hist")
            boardRate.cd(2)
            hBoardRateNorm.Draw("e")
            # add evt number
            hBoardRate.SetTitle(f"{canvasName}Rate: evt {i}")
            hBoardRateNorm.SetTitle(f"{canvasName}RateNorm: evt {i}")
            boardRate.Modified()
            boardRate.Update()
            # save on root file
            task.wrthisto(hBoardRate, f"{canvasName}_Rate")
            task.wrthisto(hBoardRateNorm, f"{canvasName}_Rate_norm")

        #if end of events in file
        if(i >= h.eventEnd):
            boardRate.cd(1)
            hBoardRate.Draw("hist")
            boardRate.cd(2)
            hBoardRateNorm.Draw("e")
            # add evt number
            hBoardRate.SetTitle(f"{canvasName}Rate: evt {i}")
            hBoardRateNorm.SetTitle(f"{canvasName}RateNorm: evt {i}")
            boardRate.Modified()
            boardRate.Update()
            # save on root file
            task.wrthisto(hBoardRate, f"{canvasName}_Rate")
            task.wrthisto(hBoardRateNorm, f"{canvasName}_Rate_norm")

            #if end of file, exit
            if i == 999999:
                print(f"{canvasName}_Rate event number : 999999. End of file. Timer = {t.perf_counter()-startT}",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
                #refresh graph?  if not, do not reset t0
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()
        
       # wait for reader 
        while(h.iRead<=i):
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
            print(f"i =\t{i};\ttime =\t{time};\ttime = {time/tps} s",flush=True)
            print(f"t0 =\t{t0};\t{t0/tps} s",flush=True)
            print(f"ts =\t{ts};\t{ts/tps}",flush=True)
            print(f"{canvasName} grabbed a bad value. Skipping...",flush=True)
            continue
        
        #count how many hits for the board  
        weight=0
        for bid in boardArr:
            if bid == boardNumber:
                weight = weight +1
                
        #normalized rate
        hBoardRateNorm.Fill((ts-t0)/tps,weight/binwidth)
        #unnormalized rate
        hBoardRate.Fill((ts-t0)/tps,weight)

        #reset hist if past time range
        if (ts-t0)/tps >= h.timeRange:
           # avoid random big numbers (better fix to do) 
            if (ts-t0)/tps >= 2*h.timeRange:
                print(f"{canvasName} was about to set t0 = {ts/tps} s from {t0/tps} s",flush=True)
                continue
            t0 = ts
            hBoardRate.Reset()
            hBoardRateNorm.Reset()
           # print(f"{canvasName} set t0 = {t0/tps} s",flush=True)
            

def plotDetHitRate(canvasName,boardId):
    startT = t.perf_counter()
    bId=[] # array with selected boards 

    for b in range(0,len(boardId)):
            #if there's just one board:
            if type(boardId[b]) == int:
                bId.append(boardId[b])
            #if there are multiple boards:
            else:
                #for each board:
                for d in range(0,len(boardId[b])):
                    bId.append(boardId[b][d])

    SbId=set(bId)

    t0 = h.t0
    run = True
    stuck = 0
    tps = h.tsPerSec
    binwidth = h.rateBinwidth
    iupdate = h.updateIndex

    #set hists
    hBoardRate = TH1D(f"{canvasName}Rate",f"{canvasName} Hits per {binwidth} s",int(h.timeRange/binwidth),0,h.timeRange)
    hBoardRateNorm = TH1D(f"{canvasName}RateNorm",f"{canvasName} Hits per second",int(h.timeRange/binwidth),0,h.timeRange)
    hBoardRate.GetXaxis().SetTitle("time (s)")
    hBoardRate.GetYaxis().SetTitle(f"hits per {binwidth} s")
    hBoardRateNorm.GetXaxis().SetTitle("time (s)")
    hBoardRateNorm.GetYaxis().SetTitle("hits per second")
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

        #update
        if i%iupdate == 0:
            print(f"{canvasName}_Rate event number : {i}, Timer = {t.perf_counter()-startT}",flush=True)
            boardRate.cd(1)
            hBoardRate.Draw("hist")
            boardRate.cd(2)
            hBoardRateNorm.Draw("e")
            # add evt number
            hBoardRate.SetTitle(f"{canvasName}Rate: evt {i}")
            hBoardRateNorm.SetTitle(f"{canvasName}RateNorm: evt {i}")
            boardRate.Modified()
            boardRate.Update()
            # save on root file
            task.wrthisto(hBoardRate, f"{canvasName}_Rate")
            task.wrthisto(hBoardRateNorm, f"{canvasName}_Rate_norm")

        #if end of events in file
        if(i >= h.eventEnd):
            boardRate.cd(1)
            hBoardRate.Draw("hist")
            boardRate.cd(2)
            hBoardRateNorm.Draw("e")
            # add evt number
            hBoardRate.SetTitle(f"{canvasName}Rate: evt {i}")
            hBoardRateNorm.SetTitle(f"{canvasName}RateNorm: evt {i}")
            boardRate.Modified()
            boardRate.Update()
            # save on root file
            task.wrthisto(hBoardRate, f"{canvasName}_Rate")
            task.wrthisto(hBoardRateNorm, f"{canvasName}_Rate_norm")

            #if end of file, exit
            if i == 999999:
                print(f"{canvasName}_Rate event number : 999999. End of file. Timer = {t.perf_counter()-startT}",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
                #refresh graph?  if not, do not reset t0
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()
        
       # wait for reader 
        while(h.iRead<=i):
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
        
        SboardArr = set(boardArr)

        #Check if the selected detector is hit
        if len(SbId.intersection(SboardArr))<1:
            h.iArr[iNext] += 1
            continue

        #keep time in original units until filling hist
        h.iArr[iNext] += 1

        #catch bad events
        time = ts-t0
        if time < 0:
            print("---------------------------------------------------------bad")
            print(f"i =\t{i};\ttime =\t{time};\ttime = {time/tps} s",flush=True)
            print(f"t0 =\t{t0};\t{t0/tps} s",flush=True)
            print(f"ts =\t{ts};\t{ts/tps}",flush=True)
            print(f"{canvasName} grabbed a bad value. Skipping...",flush=True)
            continue
        
        weight=0
        for b in boardArr:
            if b in SbId:
                weight += 1

          
        #normalized rate
        hBoardRateNorm.Fill((ts-t0)/tps,weight/binwidth)
        #unnormalized rate
        hBoardRate.Fill((ts-t0)/tps,weight)

        #reset hist if past time range
        if (ts-t0)/tps >= h.timeRange:
           # avoid random big numbers (better fix to do) 
            if (ts-t0)/tps >= 2*h.timeRange:
                print(f"{canvasName} was about to set t0 = {ts/tps} s from {t0/tps} s",flush=True)
                continue
            t0 = ts
            hBoardRate.Reset()
            hBoardRateNorm.Reset()
           # print(f"{canvasName} set t0 = {t0/tps} s",flush=True)
            