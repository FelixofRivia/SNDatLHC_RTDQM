from ROOT import TH1D, TCanvas,TFile, gDirectory, gSystem, gStyle
import time as t
import Scripts.header as h
import Scripts.tasks as task
import numpy as np
import sys
import os


def readEntry():
    #holder = sys.stdout

    while(h.updatingFile):
        t.sleep(10)
    h.myDir = gDirectory.Get('data')
    i = h.eventStart
    h.iRead = i
    while (True):
    #if end of file, try to open next file
        if i == 999999:
            print("event = 999999. End of file.", flush=True)
            task.updateFileNumber()
            while(True):
                if (0 in h.iArr or h.i==0):
                    t.sleep(3)
                else: 
                    break
            h.waitingEnd = True
            while(h.waitingEnd):
                # if every thread has finished
                if (h.iArr.count(999999)==len(h.iArr) and h.i==999999):
                    try:
                        print("Trying to open new file...", flush=True)
                        task.reopenFile()
                        # reset index for every thread
                        task.updateAllEvents()
                        h.i = 0
                        for n in range(len(h.iArr)):
                            h.iArr[n] = 0
                        i = h.eventStart
                        h.iRead = i
                        h.waitingEnd = False
                    except:
                        t.sleep(2)
                else:
                    t.sleep(10)
            print("NEW FILE", flush=True)    
        if i >= h.eventEnd:           
            #if end of a set range
            if h.isSetRange == True:
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
                reopen = True
                while (reopen):
                    task.reopenFile()
                    try:
                        h.myDir = gDirectory.Get('data')
                        reopen = False
                    except:
                        print("Failed to update file ... trying again", flush = True)
                        t.sleep(3)
                print("opened",flush=True)
                # h.myDir.Refresh()
                # h.file.ReadKeys()
                h.readingTree=False
                # gDirectory.ReadKeys()

                if h.myDir.GetEntriesFast() - 1 > h.eventEnd:
                    h.eventEnd = h.myDir.GetEntriesFast() - 1
                    waiting = False

                print(f"eventEnd now = {h.eventEnd}", flush=True)

        i += 1
        h.iRead = i

def avoidOverlap(i,iNext):
    #while sharing a value with rate or another thread
    while(i > h.i):   
        t.sleep(5)
        
        
# def avoidOverlap(i,iNext):
#     #while sharing a value with rate or another thread
#     while(i == h.i or (h.iArr.count(i)>1 and i>0)):
#         if i == h.i:
#             t.sleep(1)
#         else:
#             t.sleep(iNext*.05)

