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
#import Scripts.luminosity as lum
import Scripts.reader as read
import Scripts.valuePlots as val
import Scripts.timeAlign as align


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('runNumber', type=str)
    parser.add_argument('fileNumber', type=str)
   # parser.add_argument('serverNumber',type=str)
    parser.add_argument('beammode',type=str)
    args = parser.parse_args()

    h.fileN = int(args.fileNumber)
    h.runN = int(args.runNumber)

    #make run (file) number 6 (4) digits , 0 padded
    runNumber = args.runNumber.rjust(6,"0")
    fileNumber = args.fileNumber.rjust(4,"0")
    beammode = args.beammode.lower()
    print(f"Beammode = {beammode} --------------------------",flush=True)

    TH1.AddDirectory(False)
   # h.filedir = f"root://snd-server-1:1094///mnt/raid1/data_online/" #online
   # h.filedir = f"/home/sndmon/QtDqmp/Data/"   #local new   
    #h.filedir = f"/home/sndmon/Snd/Data/"   #local old
   # h.filedir = f"/home/sndecs/RunData/" #local TB
    h.filedir = f"./../Data/"
    if beammode=="test":
        h.filedir = f"./Data/" #local test
        h.confName = "board_mapping_local.json"

    h.filename = h.filedir + f"run_{runNumber}/data_{fileNumber}.root"

    h.wrtfile = ROOT.TFile.Open(h.wrtfilename, "RECREATE")
    print(f"creating write file: {h.wrtfilename}",flush=True)
    h.wrtfile.Close()

    h.file = ROOT.TFile.Open(h.filename,'r')

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
    #lumi = threading.Thread(target=lum.main)

    rateVeto = threading.Thread(target=r.plotDetHitRate, args = ("Veto",h.vetoId))
    rateSciFi = threading.Thread(target=r.plotDetHitRate, args=("Scifi",h.sciFiId))
    rateUS = threading.Thread(target=r.plotDetHitRate, args=("US",h.usId))
    rateDS   = threading.Thread(target=r.plotDetHitRate, args=("DS",h.dsId))
    rateBM = threading.Thread(target=r.plotDetHitRate, args=("BM",h.beammonId))

    sciFiCh = threading.Thread(target=hit.plotHitsChDet, args=("SciFi",h.sciFiId,h.sciFiName))
    vetoCh = threading.Thread(target=hit.plotHitsChannel, args=("Veto",h.vetoId))
    usCh = threading.Thread(target=hit.plotHitsChDet, args=("US",h.usId,h.usName))
    dsCh = threading.Thread(target=hit.plotHitsChDet, args=("DS",h.dsId,h.dsName))
    bmCh = threading.Thread(target=hit.plotHitsChDet, args=("BM",h.beammonId,h.beammonName))

    hitsTot = threading.Thread(target=hit.plotHitsBoard, args=("Total",h.totId,h.totName))
    hitsVeto = threading.Thread(target=hit.plotHitsBoard, args=("Veto",h.vetoId,h.vetoName))
    hitsSciFi = threading.Thread(target=hit.plotHitsBoard, args=("SciFi",h.sciFiId,h.sciFiName))
    hitsUS = threading.Thread(target=hit.plotHitsBoard, args=("US",h.usId,h.usName))
    hitsDS = threading.Thread(target=hit.plotHitsBoard, args=("DS",h.dsId,h.dsName))
    hitsBM = threading.Thread(target=hit.plotHitsBoard, args=("BM",h.beammonId,h.beammonName))

    hitsBarDSL = threading.Thread(target=hit.plotHitsBar, args=("DSL",h.dsId[0],[0,1]))
    hitsBarDSR = threading.Thread(target=hit.plotHitsBar, args=("DSR",h.dsId[0],[6,7]))
    
    mapSciFi1 = threading.Thread(target=map.plot2DSciFi,args=(h.sciFiId[0][0],h.sciFiId[1][0],"SciFi1"))
    hitMap = threading.Thread(target=map.plot2DMap, args=(11,29,[0,1,2,3,5,6,7],[0,1,2,3,5,6,7],"SciFi_1_hitmap",1,1))
    hitMapDSV = threading.Thread(target=map.plot2DMap, args=(48,48,[2,3],[2,3],"DSVhitmap",1,1))
    valDS1 = threading.Thread(target=val.plotValueBoardMS, args=("DS1",h.dsId[0],[0,1,2,3,6,7]))
    valDS1V = threading.Thread(target=val.plotValueBoardMS, args=("DS1V",h.dsId[0],[2,3]))
    valDS1V2 = threading.Thread(target=val.plotValueBoardMS, args=("DS1V2",h.dsId[0],[2]))
    valDS1V3 = threading.Thread(target=val.plotValueBoardMS, args=("DS1V3",h.dsId[0],[3]))
    valDS1L = threading.Thread(target=val.plotValueBoardMS, args=("DS1L",h.dsId[0],[6,7]))
    valDS1R = threading.Thread(target=val.plotValueBoardMS, args=("DS1R",h.dsId[0],[0,1]))


    valUS1 = threading.Thread(target=val.plotValueBoardMS, args=("US1",h.usId[0],[4,5,6,7]))
    valUS2 = threading.Thread(target=val.plotValueBoardMS, args=("US2",h.usId[0],[0,1,2,3]))
    valUS3 = threading.Thread(target=val.plotValueBoardMS, args=("US3",h.usId[1],[0,1,4,5]))
    valUS4 = threading.Thread(target=val.plotValueBoardMS, args=("US4",h.usId[2],[0,1,2,3]))
    #valUS5 = threading.Thread(target=val.plotValueBoardMS, args=("US5",h.usId[3],[0,1,2,3]))

    scatValUS1 = threading.Thread(target=val.plotScatterValue, args=(h.usId[0],h.usId[0],[6,7],[4,5],"US1L","US1R"))
    scatValUS2 = threading.Thread(target=val.plotScatterValue, args=(h.usId[0],h.usId[0],[2,3],[0,1],"US2L","US2R"))
    scatValUS3 = threading.Thread(target=val.plotScatterValue, args=(h.usId[1],h.usId[1],[4,5],[0,1],"US3L","US3R"))
    scatValUS4 = threading.Thread(target=val.plotScatterValue, args=(h.usId[2],h.usId[2],[2,3],[0,1],"US4L","US4R"))
    #scatValUS5 = threading.Thread(target=val.plotScatterValue, args=(h.usId[3],h.usId[3],[2,3],[0,1],"US5L","US5R"))
    scatValUS1R2R = threading.Thread(target=val.plotScatterValue, args=(h.usId[0],h.usId[0],[4,5],[0,1],"US1R","US2R"))
    scatValUS1L2L = threading.Thread(target=val.plotScatterValue, args=(h.usId[0],h.usId[0],[6,7],[2,3],"US1L","US2L"))
    scatValUS1R1V = threading.Thread(target=val.plotScatterValue, args=(h.usId[0],h.dsId[0],[4,5],[2,3],"US1R","DS1V"))
  #  valScifi1x = threading.Thread(target=val.plotValueBoardMB, args=("SciFi1",h.sciFiId[0]))
    alignUS = threading.Thread(target=align.plotTimeAlign, args=("US",h.usId))

   # planeUS = threading.Thread(target=hit.plotHitsPlaneMS, args=("US",h.usId,h.usPName, h.usSlot))
    planeUS = threading.Thread(target=hit.plotHitsPlaneMS, args=("US",h.usId,[['us_1L','us_1R','us_2L','us_2R'], ['us_3L','us_3R'], ['us_4L','us_4R'], ['us_5L','us_5R']], [[[6, 7],[ 4, 5], [2, 3],[ 0, 1]], [[4, 5],[ 0, 1]], [[2, 3],[ 0, 1]], [[2, 3],[ 0, 1]]]))
   # planeDS = threading.Thread(target=hit.plotHitsPlaneMS, args=("DS",h.dsId,h.dsPName, h.dsSlot))
    planeDS = threading.Thread(target=hit.plotHitsPlaneMS, args=("DS",h.dsId,[['ds_1hL','ds_1hR', 'ds_1v']], [[[6, 7],[ 0, 1], [2, 3]]]))
    planeSciFi= threading.Thread(target=hit.plotHitsPlaneMB, args=("SciFi",h.sciFiId,h.sciFiName))

   # print(h.sciFiId)
    # print(h.dsPName)
    # print(h.dsSlot)
    flags = task.read_csv_file("./plot_config.csv")
    #reader should ALWAYS be running!
    reader.start()   
    #start threads

    # rateVeto.start()
    if task.return_flag(flags, "rateSciFi")==1: 
      rateSciFi.start() 
    if task.return_flag(flags, "rateUS")==1:
      rateUS.start() 
    if task.return_flag(flags, "rateDS")==1:
      rateDS.start()
    if task.return_flag(flags, "rateBM")==1:
      rateBM.start()
    
    # hitsVeto.start()
    if task.return_flag(flags, "hitsTot")==1:
      hitsTot.start()
    if task.return_flag(flags, "hitsSciFi")==1:
      hitsSciFi.start()
    if task.return_flag(flags, "hitsUS")==1:
      hitsUS.start()
    if task.return_flag(flags, "hitsDS")==1:
      hitsDS.start()
    if task.return_flag(flags, "hitsBM")==1:
      hitsBM.start()

    hitsBarDSL.start()
    # hitsBarDSR.start()

    #vetoCh.start()
    if task.return_flag(flags, "sciFiCh")==1:
      sciFiCh.start()
    if task.return_flag(flags, "usCh")==1:             
      usCh.start()
    if task.return_flag(flags, "dsCh")==1:
      dsCh.start()
    if task.return_flag(flags, "bmCh")==1:
      bmCh.start() 


   # hitMapDSV.start()
    # hitMap.start()
   # valDS1.start()
   # valDS1V2.start()
   # valDS1V3.start()
    if task.return_flag(flags, "mapSciFi1")==1:
      mapSciFi1.start()
    if task.return_flag(flags, "valUS1")==1:
      valUS1.start()
    if task.return_flag(flags, "valUS2")==1:
      valUS2.start()
    if task.return_flag(flags, "valUS3")==1:
      valUS3.start()
    if task.return_flag(flags, "valUS4")==1:
      valUS4.start()
    if task.return_flag(flags, "valUS5")==1:
      valUS5.start()
    if task.return_flag(flags, "valDS1V")==1:
      valDS1V.start()
    if task.return_flag(flags, "valDS1L")==1:
      valDS1L.start()
    if task.return_flag(flags, "valDS1R")==1:
      valDS1R.start()
      

   # valScifi1x.start()
    if task.return_flag(flags, "scatValUS1")==1:
      scatValUS1.start()
    if task.return_flag(flags, "scatValUS2")==1:
      scatValUS2.start()
    if task.return_flag(flags, "scatValUS3")==1:
      scatValUS3.start()
    if task.return_flag(flags, "scatValUS4")==1:
      scatValUS4.start()
    if task.return_flag(flags, "scatValUS5")==1:
      scatValUS5.start()
    if task.return_flag(flags, "scatValUS1R2R")==1:
      scatValUS1R2R.start()
    if task.return_flag(flags, "scatValUS1L2L")==1:
      scatValUS1L2L.start()
    if task.return_flag(flags, "scatValUS1R1V")==1:
      scatValUS1R1V.start()

    if task.return_flag(flags, "alignUS")==1:
      alignUS.start()

    if task.return_flag(flags, "planeUS")==1:
      planeUS.start()
    if task.return_flag(flags, "planeDS")==1:
      planeDS.start()
    if task.return_flag(flags, "planeSciFi")==1:
      planeSciFi.start()

    #if "stable" in args.beammode:
   # lumi.start()

    #rate should ALWAYS be running!
    rate.start()
    while(True):
        if (gSystem.ProcessEvents()):
            break
