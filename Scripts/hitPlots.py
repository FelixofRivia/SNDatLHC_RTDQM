from ROOT import TH1D, TCanvas,TFile, gDirectory, gSystem, gStyle
import numpy as np
import time as t
import Scripts.header as h
import Scripts.tasks as task
import math
import Scripts.reader as read

hArrUSHitsPerCh = []
hArrDSHitsPerCh = []
hArrSciFiHitsPerCh = []
hArrBMHitsPerCh = []
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
    iupdate = h.updateIndex
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
                # add evt number
                eval(f"hArr{canvasName}HitsPerCh")[n-1].SetTitle(f"{canvasName}HitsPerCh: evt {i}")
                task.wrthisto(eval(f"hArr{canvasName}HitsPerCh")[n-1], f"{canvasName}{n}_Hits_per_channel")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            #task.wrthisto(hitsPerChannel, f"{canvasName}_hits_per_channel.png")

            if i == 999999:
                print(f"{canvasName}_Hits_per_channel event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()


        #update histograms
        if i%iupdate == 0:
            print(f"{canvasName}_Hits_per_channel event number : {i}",flush=True)
            for n in range(1,nCanv+1):
                hitsPerChannel.cd(n)
                eval(f"hArr{canvasName}HitsPerCh")[n-1].Draw("bar hist")
                # add evt number
                eval(f"hArr{canvasName}HitsPerCh")[n-1].SetTitle(f"{canvasName}HitsPerCh: evt {i}")
                task.wrthisto(eval(f"hArr{canvasName}HitsPerCh")[n-1], f"{canvasName}{n}_Hits_per_channel")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            #task.wrtcanvas(hitsPerChannel, f"{canvasName}_hits_per_channel.png")


        # wait for reader 
        while(h.iRead<=i):
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
            if type(boardId[b]) == int:
                for j, bn in enumerate(boardID):
                    if bn == boardId[b]:
                        ch = 64*tofID[j] + tofChannel[j]  
                        eval(f"hArr{canvasName}HitsPerCh")[b].Fill(ch,1)
                
            #if there are multiple boards:
            else:
                #for each board:
                for d in range(0,len(boardId[b])):
                    for j, bn in enumerate(boardID):
                        if bn == boardId[b][d]:
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

    eventStart = h.eventStart
    iupdate = h.updateIndex

    i = eventStart
    run = True
    iNext = len(h.iArr)
    h.iArr.append(i)
    #loop through all entries
    while(run):
        i = h.iArr[iNext]
        #update
        if i%iupdate == 0:
            print(f"{canvasName}_Hits_per_channel number : {i}",flush=True)
            hHitsPerChannel.Draw("bar hist")
            # add evt number
            hHitsPerChannel.SetTitle(f"{canvasName}HitsPerChannel: evt {i}")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            task.wrthisto(hHitsPerChannel, f"{canvasName}_Hits_per_channel")

        if(i >= h.eventEnd):
            #update
            hHitsPerChannel.Draw("bar hist")
            # add evt number
            hHitsPerChannel.SetTitle(f"{canvasName}HitsPerChannel: evt {i}")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            task.wrthisto(hHitsPerChannel, f"{canvasName}_Hits_per_channel")

            if i == 999999:
                print(f"{canvasName}_Hits_per_channel event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()
            
            
        # wait for reader 
        while(h.iRead<=i):
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
        
        boardID = np.uint8(h.myDir.board_id)
        #Check if the selected board is hit
        if boardNumber not in boardID:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue

        tofChannel = np.uint8(h.myDir.tofpet_channel)
        tofID = np.uint8(h.myDir.tofpet_id)
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
    
    eventStart = h.eventStart
    iupdate = h.updateIndex
        
    #initialize canvas and histograms
    hHitsPerBoard = TH1D(f"{canvasName}HitsPerBoard",f"{canvasName} Hits per board",len(boardId),0,len(boardId))
    hits_per_board = TCanvas(f"{canvasName}_hits_per_board","hitsPerBoard",800,400)
    hHitsPerBoard.SetMinimum(0)
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
        if(i >= h.eventEnd):
            hHitsPerBoard.Draw("bar hist") 
            # add evt number
            hHitsPerBoard.SetTitle(f"{canvasName} Hits per Board: evt {i}")
            hits_per_board.Modified()
            hits_per_board.Update()
            # save on root file
            task.wrthisto(hHitsPerBoard, f"{canvasName}_Hits_per_board")

            if i == 999999:
                print(f"{canvasName}_Hits_per_board event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%iupdate == 0:
            print(f"{canvasName}_Hits_per_board event number : {i}",flush=True)
            hHitsPerBoard.Draw("bar hist") 
            # add evt number
            hHitsPerBoard.SetTitle(f"{canvasName} Hits per Board: evt {i}")
            hits_per_board.Modified()
            hits_per_board.Update()
            # save on root file
            #task.wrtcanvas(hits_per_board, f"{canvasName}_hits_per_board.png")
            task.wrthisto(hHitsPerBoard, f"{canvasName}_Hits_per_board")

        #initialize plot
        if i == h.eventStart:
            for b in range(len(boardId)):  
                if type(boardId[b]) == int:
                    hHitsPerBoard.Fill(f"board_{boardId[b]}",0)
                else:
                    for d in range(len(boardId[b])):
                        hHitsPerBoard.Fill(f"board_{boardId[b][d]}",0)

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
        h.readingTree = False #----------------------------------------end flag

        #for each set of boards
        for b in range(0,len(boardId)):
            #if there's just one board:
            if type(boardId[b]) == int:
                bn =boardId[b] 
               # count how many hits 
                weight=0
                for bid in boardArr:
                    if bid == bn:
                        weight = weight +1

                hHitsPerBoard.Fill(f"board_{boardId[b]}",weight)
            #if there are multiple boards:
            else:
                #for each board:
                for d in range(0,len(boardId[b])):
                    bn = boardId[b][d] # I need just the number
                    # count how many hits 
                    weight=0
                    for bid in boardArr:
                        if bid == bn:
                            weight = weight +1

                    hHitsPerBoard.Fill(f"board_{boardId[b][d]}",weight)

        h.iArr[iNext] += 1

###################################################################################
########################## Plot Hits per plane (multislot) ####################################
###################################################################################
def plotHitsPlaneMS(canvasName, boardId, detPName, detSlot):
    startT=t.perf_counter()
    eventStart = h.eventStart
    iupdate = h.updateIndex
        
    #initialize canvas and histograms
    hHitsPerPlane = TH1D(f"{canvasName}HitsPerPlane",f"{canvasName} Hits per plane",len(boardId),0,len(boardId))
    hits_per_plane = TCanvas(f"{canvasName}_hits_per_plane","hitsPerPlane",800,400)
    hHitsPerPlane.SetMinimum(0)
    hHitsPerPlane.GetXaxis().SetTitle("plane")
    hHitsPerPlane.GetYaxis().SetTitle("hits")
    hHitsPerPlane.SetFillColor(38)
    gStyle.SetOptStat("ne")

    #initialize plot
    for b in range(len(detPName)):  
        for d in range(len(detPName[b])):
            hHitsPerPlane.Fill(detPName[b][d],0)
    
    run = True
    i = eventStart
    iNext = len(h.iArr)
    h.iArr.append(i)

    while(run):
        i = h.iArr[iNext]
        if(i >= h.eventEnd):
            hHitsPerPlane.Draw("bar hist") 
            # add evt number
            hHitsPerPlane.SetTitle(f"{canvasName} Hits per Plane: evt {i}")
            hits_per_plane.Modified()
            hits_per_plane.Update()
            # save on root file
            task.wrthisto(hHitsPerPlane, f"{canvasName}_Hits_per_plane")

            if i == 999999:
                print(f"{canvasName}_Hits_per_plane event number : 999999. End of file. Timer = {t.perf_counter()-startT}",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%iupdate == 0:
            print(f"{canvasName}_Hits_per_plane event number : {i}, Timer = {t.perf_counter()-startT}",flush=True)
            hHitsPerPlane.Draw("bar hist") 
            # add evt number
            hHitsPerPlane.SetTitle(f"{canvasName} Hits per Plane: evt {i}")
            hits_per_plane.Modified()
            hits_per_plane.Update()
            # save on root file
            #task.wrtcanvas(hits_per_board, f"{canvasName}_hits_per_board.png")
            task.wrthisto(hHitsPerPlane, f"{canvasName}_Hits_per_plane")

        # wait for reader 
        while(h.iRead<=i):
            t.sleep(5)

        #while sharing a value with rate or another thread
        read.avoidOverlap(i,iNext)

        while(h.readingTree):
            t.sleep(0)
        h.readingTree = True #--------------------------------------------start flag
        #h.lock.acquire()
        # load in value. If invalid (<= 0), discard
        bb = h.myDir.GetEntry(i)
        if bb <= 0:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue

        # load all hit boards 
        boardArr=np.uint8(h.myDir.board_id)
        tofID = np.uint64(h.myDir.tofpet_id)
        #h.lock.release()
        h.readingTree = False #----------------------------------------end flag
        #for each set of boards
        for b in range(0,len(boardId)):
            for d in range(0,len(boardArr)):
                if boardArr[d] == boardId[b]:
                    for s in range(0,len(detSlot[b])):
                        if tofID[d] in detSlot[b][s]:
                            hHitsPerPlane.Fill(detPName[b][s],1)

        h.iArr[iNext] += 1

###################################################################################
########################## Plot Hits per plane (multiboard) ####################################
###################################################################################
def plotHitsPlaneMB(canvasName, boardId, detName):
    startT = t.perf_counter()
    eventStart = h.eventStart
    iupdate = h.updateIndex
        
    #initialize canvas and histograms
    hHitsPerPlane = TH1D(f"{canvasName}HitsPerPlane",f"{canvasName} Hits per plane",len(boardId),0,len(boardId))
    hits_per_plane = TCanvas(f"{canvasName}_hits_per_plane","hitsPerPlane",800,400)
    hHitsPerPlane.SetMinimum(0)
    hHitsPerPlane.GetXaxis().SetTitle("plane")
    hHitsPerPlane.GetYaxis().SetTitle("hits")
    hHitsPerPlane.SetFillColor(38)
    gStyle.SetOptStat("ne")

    #initialize plot
    for name in detName:  
        hHitsPerPlane.Fill(name,0)
    
    run = True
    i = eventStart
    iNext = len(h.iArr)
    h.iArr.append(i)


    while(run):
        startT = t.perf_counter()
        i = h.iArr[iNext]
        if(i >= h.eventEnd):
            hHitsPerPlane.Draw("bar hist") 
            # add evt number
            hHitsPerPlane.SetTitle(f"{canvasName} Hits per Plane: evt {i}, Timer = {t.perf_counter()-startT}")
            hits_per_plane.Modified()
            hits_per_plane.Update()
            # save on root file
            task.wrthisto(hHitsPerPlane, f"{canvasName}_Hits_per_plane")

            if i == 999999:
                print(f"{canvasName}_Hits_per_plane event number : 999999. End of file. Timer = {t.perf_counter()-startT}",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%iupdate == 0:
            print(f"{canvasName}_Hits_per_plane event number : {i}",flush=True)
            hHitsPerPlane.Draw("bar hist") 
            # add evt number
            hHitsPerPlane.SetTitle(f"{canvasName} Hits per Plane: evt {i}")
            hits_per_plane.Modified()
            hits_per_plane.Update()
            # save on root file
            #task.wrtcanvas(hits_per_board, f"{canvasName}_hits_per_board.png")
            task.wrthisto(hHitsPerPlane, f"{canvasName}_Hits_per_plane")

        # wait for reader 
        while(h.iRead<=i):
            t.sleep(5)

        #while sharing a value with rate or another thread
        read.avoidOverlap(i,iNext)

        while(h.readingTree):
            t.sleep(0)
        h.readingTree = True #--------------------------------------------start flag
        # load in value. If invalid (<= 0), discard
        bb = h.myDir.GetEntry(i)
        if bb <= 0:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue

        # load all hit boards 
        boardArr=np.uint8(h.myDir.board_id)
        #h.lock.release()
        h.readingTree = False #----------------------------------------end flag


        #for each set of boards
        for b in range(0,len(boardArr)):
            for d in range(0,len(boardId)):
                if boardArr[b] in boardId[d]:
                    hHitsPerPlane.Fill(detName[d],1)
                    
        h.iArr[iNext] += 1

###################################################################################
########################## Plot Hits per Bar #######################
###################################################################################
def plotHitsBar(canvasName,boardNumber,tof_Id):
    
    chMap = task.read_csv_file("./Scripts/DS_SiPM_mapping.csv")

    hHitsPerChannel = TH1D(f"{canvasName}HitsPerChannel",f"{canvasName} Hits per channel",60,0,60)
    hHitsPerChannel.GetXaxis().SetTitle("bar number")
    hHitsPerChannel.GetYaxis().SetTitle("hits")
    hHitsPerChannel.SetFillColor(38)
    hitsPerChannel = TCanvas(f"{canvasName}_hits_per_bar",f"{canvasName} hits per bar",600,800)
    gStyle.SetOptStat("ne")

    eventStart = h.eventStart
    iupdate = h.updateIndex

    i = eventStart
    run = True
    iNext = len(h.iArr)
    h.iArr.append(i)
    #loop through all entries
    while(run):
        i = h.iArr[iNext]
        #update
        if i%iupdate == 0:
            print(f"{canvasName}_Hits_per_bar number : {i}",flush=True)
            hHitsPerChannel.Draw("bar hist")
            # add evt number
            hHitsPerChannel.SetTitle(f"{canvasName}HitsPerBar: evt {i}")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            task.wrthisto(hHitsPerChannel, f"{canvasName}_Hits_per_bar")

        if(i >= h.eventEnd):
            #update
            hHitsPerChannel.Draw("bar hist")
            # add evt number
            hHitsPerChannel.SetTitle(f"{canvasName}HitsPerBar: evt {i}")
            hitsPerChannel.Modified()
            hitsPerChannel.Update()
            # save on root file
            task.wrthisto(hHitsPerChannel, f"{canvasName}_Hits_per_bar")

            if i == 999999:
                print(f"{canvasName}_Hits_per_bar event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()
            
            
        # wait for reader 
        while(h.iRead<=i):
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
        
        boardID = np.uint8(h.myDir.board_id)
        #Check if the selected board is hit
        if boardNumber not in boardID:
            h.iArr[iNext] += 1
            h.readingTree = False
            continue

        tofChannel = np.uint8(h.myDir.tofpet_channel)
        tofID = np.uint8(h.myDir.tofpet_id)
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
            if (bn == boardNumber and tofID[j] in tof_Id):
                ch = task.return_bar(chMap, tofID[j], tofChannel[j])
                if ch == -1:
                    h.iArr[iNext] += 1
                    continue
                hHitsPerChannel.Fill(ch,1)

        h.iArr[iNext] += 1