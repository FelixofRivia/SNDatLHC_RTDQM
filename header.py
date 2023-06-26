from ROOT import TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TGraph
import numpy as np


#choose how many events to display at a time
eventStart = 0
eventEnd = 5000
nEvents = eventEnd - eventStart
t0 = 0
updatingFile = False
readingTree = False
writingFile = False
waitingEnd = True
iArr = []
i = 0
iRead = 0

#choose how long the program waits to update the file after running out of events
refreshRate = 60 #sec

#conversion from timestamp to seconds
tsPerSec = 160000000 #160MHz

#choose how often to update histograms
##### WARNING: multi-canvas plotting may crash if update index too low
rateUpdate = 5000 #events
updateIndex = 50000 # 500

lumiBinWidth = 5 #sec

#choose how many seconds per bin
#choose how many seconds to display on the histogram
rateBinwidth = 60 #sec
timeRange = 2000 #sec

plotWholeRate = False #plot the whole file or just the specified range
isSetRange = False #do not try to get new events

#initialize a file
filename = ''
filedir = ''
file = TFile()
wrtfilename = "graphs.root"
wrtfile = TFile()
myDir = gDirectory.Get('data')
fileN = 0
runN = 0


totName = []
totPName = []
totSlot = []
totId = []

vetoName = []
vetoPName = []
vetoSlot = []
vetoId = []

sciFiName = []
sciFiPName = []
sciFiSlot = []
sciFiId = []

usName = []
usPName = []
usSlot = []
usId = []

dsName = []
dsPName = []
dsSlot = []
dsId = []

beammonName = []
beammonPName = []
beammonSlot = []
beammonId = []


#take board id and name corresponding arrays
#boardIdTot = ["board_58","board_11","board_17","board_28","board_29","board_3","board_30","board_23","board_2","board_25","board_16","board_14","board_18","board_22","board_27","board_4","board_15","board_9","board_5","board_8","board_50","board_49","board_46","board_40","board_20","board_21","board_10","board_6","board_19","board_13","board_36","board_7","board_60","board_52","board_41","board_42","board_55"]
#boardNameTot = ["veto","scifi_1x1","scifi_1x2","scifi_1x3","scifi_1y1","scifi_1y2","scifi_1y3","scifi_2x1","scifi_2x2","scifi_2x3","scifi_2y1","scifi_2y2","scifi_2y3","scifi_3x1","scifi_3x2","scifi_3x3","scifi_3y1","scifi_3y2","scifi_3y3","scifi_4x1","scifi_4x2","scifi_4x3","scifi_4y1","scifi_4y2","scifi_4y3","scifi_5x1","scifi_5x2","scifi_5x3","scifi_5y1","scifi_5y2","scifi_5y3","us1_us2","us3_us4","us5","ds1","ds2","ds3_ds4"]

#boardIdSciFi =   ["board_11", "board_17", "board_28", "board_29", "board_3",  "board_30", "board_23", "board_2",  "board_25", "board_16", "board_14", "board_18", "board_22", "board_27", "board_4",  "board_15", "board_9",  "board_5",  "board_8",  "board_50", "board_49", "board_46", "board_40", "board_20", "board_21", "board_10", "board_6",  "board_19", "board_13", "board_36"]
#boardNameSciFi = ["scifi_1x1","scifi_1x2","scifi_1x3","scifi_1y1","scifi_1y2","scifi_1y3","scifi_2x1","scifi_2x2","scifi_2x3","scifi_2y1","scifi_2y2","scifi_2y3","scifi_3x1","scifi_3x2","scifi_3x3","scifi_3y1","scifi_3y2","scifi_3y3","scifi_4x1","scifi_4x2","scifi_4x3","scifi_4y1","scifi_4y2","scifi_4y3","scifi_5x1","scifi_5x2","scifi_5x3","scifi_5y1","scifi_5y2","scifi_5y3"]

#boardIdUS =   ["board_7",  "board_60", "board_52"]
#boardNameUS = ["us1_us2",  "us3_us4",  "us5"]

#boardIdDS =   ["board_41","board_42","board_55"]
#boardNameDS = ["ds1",      "ds2",      "ds3_ds4"]
