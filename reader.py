from ROOT import TH1D, TCanvas,TFile, gDirectory, gSystem, gStyle
import time as t
import ROOT
import header as h
import tasks as task
import numpy as np

def readEntry():
    h.myDir = gDirectory.Get('data')
    i = h.eventStart
    h.iRead = i
    while (True):
        if i >= h.eventEnd:
            #if end of file, exit
            if i == 999999:
                print("event = 999999. End of file.", flush=True)
                exit()
            #if end of a set range
            elif h.isSetRange == True:
                print("end of range. Stopping loop...", flush=True)
                exit()
            #start loop to update events
            waiting = True
            while(waiting):
                print(f"eventEnd = {h.eventEnd}", flush=True)
                print("Reader out of events. Waiting...", flush=True)

                t.sleep(h.refreshRate)
                while (h.readingTree):
                    t.sleep(0.05)
                h.readingTree=True
                h.myDir.Refresh()
                h.file.ReadKeys()
                h.readingTree=False
                #gDirectory.ReadKeys()

                if h.myDir.GetEntriesFast() - 1 > h.eventEnd:
                    h.eventEnd = h.myDir.GetEntriesFast() - 1
                    waiting = False

                print(f"eventEnd now = {h.eventEnd}", flush=True)

        i += 1
        h.iRead = i

def avoidOverlap(i,iNext):
    #while sharing a value with rate or another thread
    while(i > h.i):   #i > h.i
        #print(f"tried to grab val, waiting...\i = {i}",flush=True)
        #print(h.iArr,flush=True)
        t.sleep(3)
        
        
# def avoidOverlap(i,iNext):
#      #while sharing a value with rate or another thread
#        while(i == h.i or len(set(h.iArr.count(i) for n in h.iArr)) > 1):
#             print(f"tried to grab val, waiting...\i = {i}",flush=True)
#             print(h.iArr,flush=True)
#             if i == h.eventEnd or i == (h.eventEnd - 1):
#                 t.sleep(h.refreshRate)
#             else:
#                 print(f"tried to grab val, waiting...\ti = {i}")
#                 print(f"eventEnd = {h.eventEnd}")
#             #if with another thread, wait by priority of a .5 second delay
#             if len(set(h.iArr.count(i) for n in h.iArr)) > 1:
#                 t.sleep(iNext*.5)
#                 break
#             #if with rate, rate always has priority
#             else:
#                 t.sleep(.25)