from wsgiref.headers import tspecials
from ROOT import TH1D, TCanvas, TFile, gDirectory, TDirectoryFile
import header as h
import time as t
import ROOT
import json

def updateFileNumber():    # for online data only
    h.fileN += 1
    fileNumber = str(h.fileN).rjust(4,"0")
    runNumber = str(h.runN).rjust(6,"0")
    h.filename = h.filedir + f"run_{runNumber}/data_{fileNumber}.root"
    print(f"New file name: {h.filename}", flush=True)

def wrtcanvas(canv, name):
    while (h.writingFile):
        t.sleep(0.1)
    h.writingFile = True
    h.wrtfile = ROOT.TFile.Open(h.wrtfilename,'UPDATE')
    h.wrtfile.WriteObject(canv, name, "overwrite")
    h.wrtfile.Close()
    h.writingFile = False

def wrthisto(histo, name):
    while (h.writingFile):
        t.sleep(0.1)
    h.writingFile = True
    h.wrtfile = ROOT.TFile.Open(h.wrtfilename,'UPDATE')
    h.wrtfile.WriteObject(histo, name, "overwrite")
    h.wrtfile.Close()
    h.writingFile = False

def reopenFile():
    print("Reopen file", flush=True)
    h.file.Close()
    h.file = ROOT.TFile.Open(h.filename,'r')

def setBeamParam(beammode):
    if beammode in 'stable beams':
        h.rateBinwidth = 30
        h.timeRange = 300
        h.rateUpdate = 50000
        h.updateIndex = 50000
    elif beammode in 'squeeze' or beammode in 'flat top':
        h.rateBinwidth = 60
        h.timeRange = 600
        h.rateUpdate = 10000
    elif beammode in 'ramp up':
        h.rateBinwidth = 60
        h.timeRange = 3600
        h.rateUpdate = 50000
    elif beammode in 'testbeam':
        h.rateBinwidth = 10
        h.timeRange = 200
        h.rateUpdate = 10000
        h.updateIndex = 10000
        h.refreshRate = 5
    else:
        h.rateBinwidth = 180
        h.timeRange = 6000
        h.rateUpdate = 500


####functions to be called in main to initialize eventEnd, eventStart, and eventRange:

#call in main if not setting eventEnd and eventStart, not using Update functions below
def setTimeRange():
    myVar = gDirectory.Get('data')
    var = myVar.GetEntry(h.eventEnd)
    tf = myVar.evt_timestamp
    var = myVar.GetEntry(h.eventStart)
    h.t0 = myVar.evt_timestamp
    h.timeRange = (h.t0-tf)/h.tsPerSec

#sets events to start from input seconds ago, leaves time range default
def updateSecondsAgo(secAgo):

    #get the latest timestamp, set latest event
    reopenFile()
    print("tasks accessing myVar")
    myVar = gDirectory.Get('data')
    h.eventEnd = myVar.GetEntriesFast() - 1
    var = myVar.GetEntry(h.eventEnd)
    tf = myVar.evt_timestamp

    #get start timestamp
    var = myVar.GetEntry(0)
    t0 = myVar.evt_timestamp
    if tf - (secAgo*h.tsPerSec) >= t0:
        h.t0 = tf - (secAgo*h.tsPerSec)
    else:
        print(f"eventStart before first event. Defaulting to eventStart = 0")
        h.t0 = t0

    #find start event
    for i in range(0,h.eventEnd):
        var = myVar.GetEntry(i)
        if myVar.evt_timestamp <= h.t0:
            continue
        h.eventStart = i
        break

#sets events between a time range relative to the latest event in the file
#sets time range to be between the two
def updateTimeRange(secAgoStart,secAgoEnd):
    #get the latest timestamp
    reopenFile()
    myVar = gDirectory.Get('data')
    h.eventEnd = myVar.GetEntriesFast() - 1
    var = myVar.GetEntry(h.eventEnd)
    tnow = myVar.evt_timestamp

    var = myVar.GetEntry(0)
    t0 = myVar.evt_timestamp

    #get initial/final timestamp
    tf = 0
    h.t0 = tnow - (secAgoStart*h.tsPerSec)

    h.isSetRange = True

    if tnow - (secAgoEnd*h.tsPerSec) >= t0:
        tf = tnow - (secAgoEnd*h.tsPerSec)
    else:
        print(f"eventEnd before first event. Defaulting to eventEnd = last event")
        tf = tnow

    if tnow - (secAgoStart*h.tsPerSec) >= t0:
        h.t0 = tnow - (secAgoStart*h.tsPerSec)
    else:
        print(f"eventStart before first event. Defaulting to eventEnd = 0")
        h.t0 = t0

    #find start event
    for i in range(0,h.eventEnd):
        var = myVar.GetEntry(i)
        if myVar.evt_timestamp < h.t0:
            continue
        h.eventStart = i
        break
    #find end event
    for i in range(h.eventStart,h.eventEnd):
        var = myVar.GetEntry(i)
        if myVar.evt_timestamp < tf:
            continue
        h.eventEnd = i
        break
    h.timeRange = (tf-h.t0)/h.tsPerSec

#sets eventStart as first file event, eventEnd as last file event
#sets time range, if boolean "plot whole rate" is true
#Best used with file that are finished, i.e. not real-time monitoring
#else can be used for hit plots
def updateAllEvents():
    #get first and last event
    print(f"file = {h.filename}")
    h.updatingFile = True
    while(h.updatingFile):
        h.myDir = gDirectory.Get('data')
        try: 
            h.eventEnd = h.myDir.GetEntriesFast() - 1
            h.updatingFile = False
        except:
            print("Tree is not ready, waiting...", flush=True)
            t.sleep(10)
            reopenFile()
    h.eventStart = 0
    var = h.myDir.GetEntry(h.eventStart)
    h.t0 = h.myDir.evt_timestamp
    var = h.myDir.GetEntry(h.eventEnd)
    tf = h.myDir.evt_timestamp
    if h.plotWholeRate:
        h.timeRange = (tf-h.t0)/h.tsPerSec
        print(f"plotting rate for full range \nhistogram might stop early if the file is active \ntimeRange = {h.timeRange}")
    print(f"t0 = {h.t0}\ttf = {tf}")

##functions to get board info from json file

def getMultislot(type):
    f = open("board_mapping.json")
    data = json.load(f)

    panelName = []
    boardSlots = []
    boardName = []
    boardId = []
    boards = []
    names = []
    slots = []

    #loop through datatype, grab boards, names, and slots
    for j in data[type]:
        j0 = j[0]
        if len(j) <= 1:
            j1 = ""
        else:
            j1 = j[1]
        boards.append(data[type][(f"{j0}{j1}")]['board'])
        names.append(f"{j0}{j1}")
        slots.append(data[type][(f"{j0}{j1}")]['slots'])

    #avoid repeated indexing
    boardsDone = []
    #for each board
    for i in range(0,len(boards)):
        #if board is not already added
        if boards[i] not in boardsDone:
            #board added
            boardsDone.append(boards[i])
            sameNameArray = []
            slotArray = []
            #boardIdArray = []
            #boardNameArray = []

            L = 0
            for l in names[i]:
                L = l
                break

            #add the name
            sameNameArray.append(f"{type}_{names[i]}")
            #boardIdArray.append(f"board_{boards[i]}")
            #boardNameArray.append(f"{type}_{L}")

            #add the slots
            tmpArr = []
            for s in slots[i]:
                if s == 'A':
                    tmpArr.append(0)
                    tmpArr.append(1)
                elif s == 'B':
                    tmpArr.append(2)
                    tmpArr.append(3)
                elif s == 'C':
                    tmpArr.append(4)
                    tmpArr.append(5)
                elif s == 'D':
                    tmpArr.append(6)
                    tmpArr.append(7)
            slotArray.append(tmpArr)

            #add the name and slots of all matching board id's
            for z in range(0,len(boards)):
                
                if boards[i] == boards[z] and i != z:
                    #boardIdArray.append(f"board_{boards[i]}")
                    #boardNameArray.append(f"{type}_{L}")
                    sameNameArray.append(f"{type}_{names[z]}")
                    boardsDone.append(boards[z])
                    tmpArr = []
                    for s in slots[z]:
                        if s == 'A':
                            tmpArr.append(0)
                            tmpArr.append(1)
                        elif s == 'B':
                            tmpArr.append(2)
                            tmpArr.append(3)
                        elif s == 'C':
                            tmpArr.append(4)
                            tmpArr.append(5)
                        elif s == 'D':
                            tmpArr.append(6)
                            tmpArr.append(7)
                    slotArray.append(tmpArr)
            #write slots, and names to each board
            boardSlots.append(slotArray)
            boardName.append(f"{type}_{L}")
            #boardId.append(f"board_{boards[i]}") #old
            boardId.append(boards[i]) #new 
            #boardId.append(boardIdArray)
            panelName.append(sameNameArray)
            #grab the first number for naming
            #boardName.append(boardNameArray)
            h.totSlot.append(slotArray)
            h.totName.append(f"{type}_{L}")
            #h.totId.append(f"board_{boards[i]}") #old 
            h.totId.append(boards[i]) #new 
            h.totPName.append(sameNameArray)
    return boardId,boardName,panelName,boardSlots

def getMultiboard(type):
    #open file
    f = open("board_mapping.json")
    data = json.load(f)

    #initialize arrays
    panelName = []
    #an array of the arrays of board id per panel
    panelBoardID = []
    #an array of arrays of all tofpet id [0-7]
    slotsArray = []
    #an array of name arrays that correspond to each board of a panel
    subPanelName = []
    #an array of board ID arrays that correspond to each panel
    boardId = []

    #for each value in e.g. SciFi
    for j in data[type]:
        #grab the index number ex. 1h or 1y or 1. Catch if only 1 long
        j0 = j[0]
        if len(j) <= 1:
            j1 = ""
        else:
            j1 = j[1]

        #grab boards of a panel e.g. Scifi's 1y boards
        boards = data[type][(f"{j0}{j1}")]['boards']

        #if e.g. Scifi1y is not already in boardname, add it
        if f"{type}{j0}{j1}" not in panelName:
            ##Naming isn't right if different panel indecies share the same board (e.g. 4v of DS)
            #if str("board_" + str(data['ds'][(f"{j0}{j1}")]['board'])) in boardId:
            #    name = boardName[]
            panelName.append(f"{type}_{j0}{j1}")
            h.totName.append(f"{type}_{j0}{j1}")
            #boardArray = []
            #add boards per panel e.g. scifi1y has 3 boards
            """
            for b in boards:
                boardArray.append(f"board_{b}")
            """
            #add the boards to each unique panel name
            boardId.append(boards)
            h.totId.append(boards)
        #make names for each subpanel corresponding to the board
        nameLength = len(boards)
        subPanelNameArray = []
        boardNameArray = []
        for i in range(1,nameLength+1):
            subPanelNameArray.append(f"{j0}{j1}{i}")
            boardNameArray.append("board_" + str(data[type][(f"{j0}{j1}")]['boards']))
        subPanelName.append(subPanelNameArray)
        slotsArray.append([0,1,2,3,4,5,6,7])
        h.totSlot.append([0,1,2,3,4,5,6,7])
        h.totPName.append(subPanelNameArray)
    return boardId,panelName,subPanelName,slotsArray

def getBoardArrays(beammode):

    #info about board arrays:
    #Board ID: Non-Scifi = single ID / Scifi = array of boardID's
    #Board Name: always a scalar of what to call the board / group of boards
    #Panel Name: always an array of panels or pieces that make up the board / group of boards
    #Slots/TofpetID: Non-Scifi = array of arrays (tofpet id per panel, multiple panels per group of boards) / Scifi: array, always [0-7] for all boards



   # add back 
   # h.vetoId, h.vetoName, h.vetoPName, h.vetoSlot = getMultislot("veto")
    h.sciFiId, h.sciFiName, h.sciFiPName, h.sciFiSlot = getMultiboard("scifi")
    h.usId, h.usName, h.usPName, h.usSlot = getMultislot("us")
    h.dsId, h.dsName, h.dsPName, h.dsSlot = getMultislot("ds")
    if beammode=="testbeam":
        h.beammonId, h.beammonName, h.beammonPName, h.beammonSlot = getMultislot("beammon")
