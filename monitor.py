from ROOT import TH1, TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TGraph
import numpy as np
import argparse
import threading
import ROOT
import os
import time as t

import Scripts.header as h
import Scripts.tasks as task
import Scripts.ratePlots as r
import Scripts.hitPlots as hit
import Scripts.hitMaps as map
import Scripts.luminosity as lum
import Scripts.reader as read
import Scripts.valuePlots as val
import Scripts.timeAlign as align


if __name__ == '__main__':
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

    #run through all the events (recommended option)
    task.updateAllEvents()

    #start from the event arg1 seconds ago, until h.timeRange
    #task.updateSecondsAgo(150)

    #plot events between arg1 and arg2 seconds ago
    #task.updateTimeRange(300,120)


    #enable root multithreading   
    nThreads = 6
    ROOT.EnableThreadSafety()
    ROOT.EnableImplicitMT(nThreads)

    print("To kill program, enter Ctrl+\\",flush=True)

    #gROOT.SetBatch(True)

    #pull board info from json file
    task.getBoardArrays(beammode)

    #define threading functions
    reader = threading.Thread(target=read.readEntry)
    rate = threading.Thread(target=r.plotGlobalEvtRate)
    lumi = threading.Thread(target=lum.main)

    rateVeto = threading.Thread(target=r.plotDetHitRate, args = ("Veto",h.vetoId))
    rateSciFi = threading.Thread(target=r.plotDetHitRate, args=("Scifi",h.sciFiId))
    rateUS = threading.Thread(target=r.plotDetHitRate, args=("US",h.usId))
    rateDS   = threading.Thread(target=r.plotDetHitRate, args=("DS",h.dsId))
    rateBM = threading.Thread(target=r.plotDetHitRate, args=("BM",h.beammonId))

    sciFiCh = threading.Thread(target=hit.plotHitsChDet, args=("SciFi",h.sciFiId,h.sciFiName))
    vetoCh = threading.Thread(target=hit.plotHitsChannel, args=("Veto",h.vetoId))
    usCh = threading.Thread(target=hit.plotHitsChDet, args=("US",h.usId,h.usName))
    dsCh = threading.Thread(target=hit.plotHitsChDet, args=("DS",h.dsId,h.dsName))
    BMCh = threading.Thread(target=hit.plotHitsChDet, args=("BM",h.beammonId,h.beammonName))

    hitsTot = threading.Thread(target=hit.plotHitsBoard, args=("Total",h.totId,h.totName))
    hitsSciFi = threading.Thread(target=hit.plotHitsBoard, args=("SciFi",h.sciFiId,h.sciFiName))
    hitsUS = threading.Thread(target=hit.plotHitsBoard, args=("US",h.usId,h.usName))
    hitsDS = threading.Thread(target=hit.plotHitsBoard, args=("DS",h.dsId,h.dsName))
    hitsBM = threading.Thread(target=hit.plotHitsBoard, args=("BM",h.beammonId,h.beammonName))

    hitMap = threading.Thread(target=map.plot2DMap, args=(11,29,[0,1,2,3,5,6,7],[0,1,2,3,5,6,7],"SciFi_1_hitmap",1,1))
    valDS = threading.Thread(target=val.plotValueBoard, args=("DS",h.dsId))
    valUS = threading.Thread(target=val.plotValueBoard, args=("US",h.usId))
    alignUS = threading.Thread(target=align.plotTimeAlign, args=("US",h.usId))

    planeUS = threading.Thread(target=hit.plotHitsPlaneMS, args=("US",h.usId,h.usPName, h.usSlot))
    planeDS = threading.Thread(target=hit.plotHitsPlaneMS, args=("DS",h.dsId,h.dsPName, h.dsSlot))
    planeSciFi= threading.Thread(target=hit.plotHitsPlaneMB, args=("SciFi",h.sciFiId,h.sciFiName))

    #reader should ALWAYS be running!
    reader.start()   

    #start threads

    #rateVeto.start() 
    #rateSciFi.start() 
    #rateUS.start() 
    #rateDS.start()
    #rateBM.start()
    
    #hitsTot.start()
    #hitsSciFi.start()
    #hitsUS.start()
    #hitsDS.start()
    #hitsBM.start()

    #vetoCh.start()
    #sciFiCh.start()             
    #usCh.start()
    #dsCh.start()
    #BMCh.start() 

    #hitMap.start()
    valDS.start()
    #valUS.start()
    #alignUS.start()

    planeUS.start()
    #planeDS.start()  
    #planeSciFi.start()

    #if "stable" in args.beammode:
    #lumi.start()

    #rate should ALWAYS be running!
    rate.start()

    while(True):
        if (gSystem.ProcessEvents()):
            break
