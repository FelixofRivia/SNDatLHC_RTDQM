from ROOT import TH1, TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TGraph
from array import array
import numpy as np
from ROOT import THttpServer
import argparse
import threading
import ROOT
import os
import time as t

import header as h
import tasks as task
import ratePlots as r
import hitPlots as hit
import hitMaps as map
import luminosity as lum
import reader as read
import valuePlots as val
import timeAlign as align

#default arguments in header, should be edited as they become parsed arguments
#add arguments for runNumber and dataNumber
parser = argparse.ArgumentParser()
parser.add_argument('runNumber', type=str)
parser.add_argument('fileNumber', type=str)
parser.add_argument('serverNumber',type=str)
parser.add_argument('beammode',type=str)
args = parser.parse_args()

h.fileN = int(args.fileNumber)
h.runN = int(args.runNumber)

#make run (file) number 6 (4) digits , 0 padded
runNumber = args.runNumber.rjust(6,"0")
fileNumber = args.fileNumber.rjust(4,"0")
serverNumber = args.serverNumber.rjust(4,"0")
beammode = args.beammode.lower()
print(f"Beammode = {beammode} --------------------------",flush=True)


h.filedir = f"root://snd-server-1:1094///mnt/raid1/data_online/" #online
#h.filedir = f"/home/sndmon/QtDqmp/Data/"   #local new
#h.filedir = f"/home/sndmon/Snd/Data/"   #local old
#h.filedir = f"/home/sndecs/RunData/" #local TB

h.filename = h.filedir + f"run_{runNumber}/data_{fileNumber}.root"

h.wrtfile = ROOT.TFile.Open(h.wrtfilename, "RECREATE")
print(f"creating write file: {h.wrtfilename}",flush=True)
h.wrtfile.Close()

h.file = ROOT.TFile.Open(h.filename,'r')
print(f"opening file first time: {h.filename}",flush=True)

task.setBeamParam(beammode)

#avoid segmentation violation when closing file
#TH1.AddDirectory(False)

#run through all the events (best for complete files)
task.updateAllEvents()

#h.plotWholeRate = True

#start from the event arg1 seconds ago, until h.timeRange
#task.updateSecondsAgo(5)

#plot events between arg1 and arg2 seconds ago
#task.updateTimeRange(240,120)

#enable root multithreading   
nThreads = 6
ROOT.EnableThreadSafety()
ROOT.EnableImplicitMT(nThreads)

print("To kill program, enter Ctrl+\\",flush=True)

#gROOT.SetBatch(True)

#load server
#go to zh-desktop:710X?top=monitoring
#serverName = f"http:{serverNumber}?top=monitoring"
#serv = THttpServer(serverName)
#serv.CreateServerThread()
#serv.Register("Graphs",h.wrtfile)

#serv.CreateEngine("fastcgi:9000")

#pull board info from json file
task.getBoardArrays(beammode)

#define threading functions
def callRateVeto():
    r.plotBoardRate("Veto",58)
def callRateDs():
    r.plotBoardRate("DS",44)
def callRateSciFi11():
    r.plotBoardRate("scifiTest",11)
def callRateSciFi36():
    r.plotBoardRate("scifiTest",36)
def callRateUS1():
    r.plotBoardRate("US1",32)
def callRateUS2():
    r.plotBoardRate("US3_4",60)
def callRateUS3():
    r.plotBoardRate("US5",52)
def callRateBM():
    r.plotBoardRate("BM",59)

def callGlobalRate():
    r.plotGlobalRate()

def callHitsTot():
    hit.plotHitsBoard("Total",h.totId,h.totName)
def callHitsSciFi():
    hit.plotHitsBoard("SciFi",h.sciFiId,h.sciFiName)
def callHitsDS():
    hit.plotHitsBoard("DS",h.dsId,h.dsName)
def callHitsUS():
    hit.plotHitsBoard("US",h.usId,h.usName)
def callHitsBM():
    hit.plotHitsBoard("BM",h.beammonId,h.beammonName)

def callChannelVeto():
    hit.plotHitsChannel("Veto",int(h.vetoId[0].strip("board_")))

def callUSCh():
    hit.plotHitsChDet("US",h.usId,h.usName)
def callDSCh():
    hit.plotHitsChDet("DS",h.dsId,h.dsName)
def callBMCh():
    hit.plotHitsChDet("BM",h.beammonId,h.beammonName)
def callSciFiCh():
    hit.plotHitsChDet("SciFi",h.sciFiId,h.sciFiName)

def callSciFi60Ch():
    hit.plotHitsChannel("SciFi",60)

def callHitMap():
    map.plot2DMap(24,53,[0,1,2,3,5,6,7],[0,1,2,3,5,6,7],"SciFi_1_hitmap",1,1)

def callValueDS():
    val.plotValueBoard("DS",h.dsId)

def callValueUS():
    val.plotValueBoard("US",["board_34"])    ##################################### us1 

def callAlignUS():
    align.plotTimeAlign("US",h.usId)


usCh = threading.Thread(target=callUSCh)
dsCh = threading.Thread(target=callDSCh)
BMCh = threading.Thread(target=callBMCh)
sciFiCh = threading.Thread(target=callSciFiCh)
#sciFi60Ch = threading.Thread(target=callSciFi60Ch)
hitMap = threading.Thread(target=callHitMap)
valDS = threading.Thread(target=callValueDS)
valUS = threading.Thread(target=callValueUS)
alignUS = threading.Thread(target=callAlignUS)

#usCh.start()
#dsCh.start()
#BMCh.start() 
#sciFiCh.start()
#sciFi60Ch.start()
#hitMap.start()
valDS.start()
#valUS.start()
alignUS.start()

def callDetectorRateSciFi():
    r.plotDetectorRate("Scifi",h.sciFiId[0][0])

def callLumi():
    lum.main()

def callReader():
    read.readEntry()

hitsTot = threading.Thread(target=callHitsTot)
hitsSciFi = threading.Thread(target=callHitsSciFi)
rateVeto = threading.Thread(target=callRateVeto)
rateDS   = threading.Thread(target=callRateDs)
vetoCh = threading.Thread(target=callChannelVeto)
hitsDS = threading.Thread(target=callHitsDS)
hitsUS = threading.Thread(target=callHitsUS)
hitsBM = threading.Thread(target=callHitsBM)
rateSciFi11 = threading.Thread(target=callRateSciFi11)
rateSciFi36 = threading.Thread(target=callRateSciFi36)
rateSciFiTot = threading.Thread(target=callDetectorRateSciFi)
rateUS1 = threading.Thread(target=callRateUS1)
rateUS2 = threading.Thread(target=callRateUS2)
rateUS3 = threading.Thread(target=callRateUS3)
rateBM = threading.Thread(target=callRateBM)

reader = threading.Thread(target=callReader)
reader.start()   # must be always active

#start threads

print(h.usId)
print(h.sciFiId)
print(h.usName)
print(h.usPName)
print(h.usSlot)
#print(h.beammonName)
# print(h.vetoPName)
#print(h.beammonId)
#print(h.beammonSlot)

#rateVeto.start() ###############################  
#rateUS1.start()
#rateUS2.start()
#rateUS3.start()
#rateDS.start()
#rateBM.start()
#hitsDS.start()  ########################### 
#hitsUS.start()  #################################### 
#hitsBM.start()
#hitsTot.start()
#hitsSciFi.start()
#vetoCh.start()            ################################ 
#rateSciFi11.start()
#rateSciFi36.start()
#rateSciFiTot.start()

#if args.beammode == 'STABLE':
lumi = threading.Thread(target=callLumi)
#lumi.start()

#print(f"update = {h.updateIndex}",flush=True)
#rate should ALWAYS be running!
rate = threading.Thread(target=callGlobalRate)
rate.start()


while(True):
    if (gSystem.ProcessEvents()):
        break
