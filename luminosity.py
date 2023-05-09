from ROOT import TH1D, TCanvas, TFile, gDirectory, gSystem
import ROOT
import header as h
import tasks as task
import ratePlots as r
#source ~/snd.sh

###################################################################################
########################## Get Status and Lumi ###################################
###################################################################################
import pydim
import sys
import time as t
from fcntl import DN_DELETE
from math import log10
import os

LumiAtlas = 0 
AtlasTime = 0 
LumiAlice = 0 
AliceTime = 0
IsAtlas   = False
plotLumi = True
BeamMode = ''

def cb_LumiAtlas(colrate, colerr, coltime):
    global LumiAtlas,IsAtlas
    #print("Lumi Atlas")
    LumiAtlas = colrate
    IsAtlas   = True

    #print(colrate)
    #print(colerr)
    #print(coltime)

    
def cb_BeamMode(now,fill):
    global plotLumi, BeamMode
    BeamMode = fill
    print("Beam Mode - ",BeamMode)
    if "STABLE BEAMS" in BeamMode:
        plotLumi = True
    print(plotLumi)


def cb_StatusAtlas(now,status):
    AtlasStatus = status
    #print("Atlas Status - ",AtlasStatus)
    
def cb_StatusAlice(now,status):
    AliceStatus = status
    #print("Alice Status - ",AliceStatus)


def cb_LumiAlice(LumiDel,LumiRec):
    #print("Lumi Alice")
    #print(LumiDel)
    #print(LumiRec)
    x = 1

def main():
    #sys.stdout = open(os.devnull, "w")
    #sys.stderr = open(os.devnull, "w")  #do not print errors
    global LumiAtlas, AtlasTime,LumiAlice,AliceTime,IsAtlas
    if not pydim.dis_get_dns_node():
        print("No Dim DNS node found. Please set the environment variable DIM_DNS_NODE", flush=True)
        sys.exit(1)
    
    res1 = pydim.dic_info_service("dip/ALICE/LHC/ExptStatus/DipData",cb_StatusAlice)
    res2 = pydim.dic_info_service("dip/ATLAS/LHC/ExptStatus/DipData",cb_StatusAtlas)
    res3 = pydim.dic_info_service("dip/acc/LHC/RunControl/BeamMode/DipData",cb_BeamMode)
    res4 = pydim.dic_info_service("dip/ALICE/LHC/FillLumi/DipData","F:1;F:1",cb_LumiAlice)
    res5 = pydim.dic_info_service("dip/ATLAS/LHC/Luminosity/DipData","F:3",cb_LumiAtlas)

 
    if not res1 or not res2 or not res3 or not res4 or not res5:
        print("There was an error registering the clients", flush=True)
        sys.exit(1)
        
    # Wait for updates
    while plotLumi:
        hLumi = TH1D("hLumi","Atlas Instant Lumi",int(h.timeRange/h.lumiBinWidth),0,h.timeRange)
        LumiCanvas = TCanvas("LumiCanvas","LumiRate",600,1200)
        LumiCanvas.Divide(1,2)
        AtlasTime = 0
        IsAtlas   = True
        while True:
            t.sleep(h.lumiBinWidth)
            AtlasTime += 1
            #print("Timeout ", LumiAtlas,IsAtlas)
            if(IsAtlas):
                IsAtlas = False
                #if(AtlasTime%5):
                hLumi.Fill(AtlasTime*h.lumiBinWidth,LumiAtlas)
                if(AtlasTime*h.lumiBinWidth == h.timeRange):
                    AtlasTime = 0
                    hLumi.Reset("ICESM")
            
            
            if(AtlasTime%h.lumiBinWidth):
                LumiCanvas.cd(1)
                hLumi.Draw("hist")
                LumiCanvas.cd(2)
                rate = r.hRateNorm
                rate.Draw()
                LumiCanvas.Modified()
                LumiCanvas.Update()

#if __name__=="__main__":
#    #global LumiAtlas, AtlasTime,LumiAlice,AliceTime,IsAtlas
#    main()