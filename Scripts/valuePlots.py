from ROOT import TH1D, TCanvas,TFile, gDirectory, gSystem, gStyle, TH2D
import numpy as np
import time as t
import Scripts.header as h
import Scripts.tasks as task
import Scripts.reader as read

def plotValueBoardMB(canvasName, boardId):
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
        if(i >= h.eventEnd):
            hValues.Draw("bar hist")
            # add evt number
            hValues.SetTitle(f"{canvasName} Value: evt {i}")
            cvalues.Modified()
            cvalues.Update()
            # save on root file
            task.wrthisto(hValues, f"{canvasName}_QDC")

            if i == 999999:
                print(f"{canvasName}_QDC event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%iupdate == 0:
            print(f"{canvasName}_QDC event number : {i}",flush=True)
            hValues.Draw("bar hist")
            # add evt number
            hValues.SetTitle(f"{canvasName} Value: evt {i}") 
            cvalues.Modified()
            cvalues.Update()
            # save on root file
            task.wrthisto(hValues, f"{canvasName}_QDC")

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
       # values=np.uint8(h.myDir.value)
        values=np.uint16(h.myDir.value)  
        h.readingTree = False #----------------------------------------end flag

        #for each set of boards
        for b in range(0,len(boardId)):
            #if there's just one board:
            if type(boardId[b]) == int:
                bn = boardId[b] # I need just the number
               # find values 
                for n in range(0,len(boardArr)):
                    if boardArr[n] == bn:
                        hValues.Fill(values[n])

            #if there are multiple boards:
            else:
                #for each board:
                for d in range(0,len(boardId[b])):
                    bn = boardId[b][d] # I need just the number
                    # find values 
                    for n in range(0,len(boardArr)):
                        if boardArr[n] == bn:
                            hValues.Fill(values[n])

        h.iArr[iNext] += 1


def plotValueBoardMS(canvasName, boardId, tofpetId):
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
        if(i >= h.eventEnd):
            hValues.Draw("bar hist")
            # add evt number
            hValues.SetTitle(f"{canvasName} Value: evt {i}")
            cvalues.Modified()
            cvalues.Update()
            # save on root file
            task.wrthisto(hValues, f"{canvasName}_QDC")

            if i == 999999:
                print(f"{canvasName}_QDC event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%iupdate == 0:
            print(f"{canvasName}_QDC event number : {i}",flush=True)
            hValues.Draw("bar hist")
            # add evt number
            hValues.SetTitle(f"{canvasName} Value: evt {i}") 
            cvalues.Modified()
            cvalues.Update()
            # save on root file
            task.wrthisto(hValues, f"{canvasName}_QDC")

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
        tofArr = np.uint8(h.myDir.tofpet_id)
        tofCh = np.uint8(h.myDir.tofpet_channel)#########################àà 

        # load all values 
       # values=np.uint8(h.myDir.value)
        values=np.uint16(h.myDir.value)  
        h.readingTree = False #----------------------------------------end flag

        # if 59 not in boardArr:  #########################################
        #     h.iArr[iNext] += 1
        #     continue
        selected=[30]

        if not any(item in selected for item in tofCh):
            h.iArr[iNext] +=1
            continue 

        #for each set of boards
        for b in range(0,len(boardArr)):
            #if there's just one board:
            if boardArr[b] == boardId:
                if tofArr[b] in tofpetId: 
                    hValues.Fill(values[b])

        h.iArr[iNext] += 1




def plotScatterValue(xBoardNumber,yBoardNumber,xtofIDs,ytofIDs,name_x,name_y):

    eventStart = h.eventStart
    iupdate = h.updateIndex

    #grab their channels
    xBins = 200
    yBins = 200
    #make 2Dhist assigned with channels
    scatVal = TH2D(str(name_y) + " vs " + str(name_x) + " values",str(name_y) + " vs " + str(name_x) + " values",xBins,0,xBins,yBins,0,yBins)
    
    #make canvas with n divisions, cd to the index of the canvas
    canvas = TCanvas(str(name_y) + "_vs_" + str(name_x) + "_values",str(name_y) + "_vs_" + str(name_x) + "_values",500,500)

    scatVal.GetXaxis().SetTitle(str(name_x) + "values (a.u)")
    scatVal.GetYaxis().SetTitle(str(name_y) + "values (a.u)")
    gStyle.SetOptStat("ne")
    
    run = True
    i = eventStart

    iNext = len(h.iArr)
    h.iArr.append(i)


    while(run):
        i = h.iArr[iNext]
        if(i >= h.eventEnd):
            scatVal.Draw("colz")
            canvas.Draw()
            # add evt number
            scatVal.SetTitle(str(name_y) + "_vs_" + str(name_x) + f"_values: evt {i}")
            canvas.Modified()
            canvas.Update()
            # save on root file
            task.wrthisto(scatVal, str(name_y) + " vs " + str(name_x) + " values")

            if i == 999999:
                print(f"{name_y}_vs_{name_x}_scatVal event number : 999999. End of file",flush=True)
                while(h.waitingEnd):
                    t.sleep(1)
                i = h.iArr[iNext]
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...")
                exit()

        #update histograms
        if i%iupdate == 0:
            print(f"{name_y}_vs_{name_x}_scatVal event number : {i}",flush=True)
            scatVal.Draw("colz")
            canvas.Draw()
            # add evt number
            scatVal.SetTitle(str(name_y) + "_vs_" + str(name_x) + f"_values: evt {i}")
            canvas.Modified()
            canvas.Update()
            # save on root file
            task.wrthisto(scatVal, str(name_y) + " vs " + str(name_x) + " values")


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
        tofID = np.uint8(h.myDir.tofpet_id)
        values=np.uint16(h.myDir.value)
        h.readingTree = False #----------------------------------------end flag

        xval=[]
        yval=[]

        if (xBoardNumber in boardArr) and (yBoardNumber in boardArr):
            for b in range(0,len(boardArr)):
                if xBoardNumber==boardArr[b] and tofID[b] in xtofIDs:
                    try:
                        xval.append(values[b])
                    except:
                        print("Value not found...ignoring",flush=True)
                if yBoardNumber==boardArr[b] and tofID[b] in ytofIDs:
                    try:
                        yval.append(values[b])
                    except:
                        print("Value not found...ignoring",flush=True)
        # fill every combination
        if len(xval)>0 and len(yval)>0:
            for x in xval:
                for y in yval:
                    scatVal.Fill(x,y)

        h.iArr[iNext] += 1