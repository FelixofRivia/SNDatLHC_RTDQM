about --------------------------------------------------------------------------------------------------------------------------

to call remotely:

ssh -C sndmon@zh-desktop QtDqmp/monitor.sh 4746 10 7108 "STABLE BEAMS"

the first argument is run number (up to 6 characters)
the second argument is file number (up to 4 characters)
the third argument is server port number (up to 4 characters)
the fourth argument is the beam status

check tasks.py function setBeamParam(beammode) to set reasonable values for beam modes
    stable beams should already be ok for a rate of ~3kHz
    can decrease the time range of other beam modes if you don't want to see the whole file
    I haven't actually tested all the beammodes, so that will probably need to be adjusted

make sure you're calling the correct task.updateEvents function
    by default, it's running all events, which is most useful for running an old file
    however, this can become an issue if you're trying to look at luminosity, as the rate and lumi WILL NOT be synched
    if you want rate and lumi to line up, it is a good idea to call the updateSecondsAgo() with an input of less than 10seconds

if you want lumi+rate plots, you NEED to run a r.plotGlobalRate thread.
    the lumi function calls the histogram from this thread

threads and current bugs ------------------------------------------------------------------------------------------------------------

    global rate has priority in terms of accessing the root file
    other threads have priority in the order the threads are started

    sometimes things crash. might be a memory issue related to large amounts of data. maybe the code will run better on lxplus?
    as of right now, it is wise to not run more than 4 canvases at a time

    hits per channel of a detector does not work for scifi; there are too many graphs
        perhaps the code can be adjusted to just write the boards of a panel, but this is not yet implemented
        it works fine for US and DS. (useless for veto)
    hits per channel of a single board seems to work fine.

    rate plots seem to work fine, except for occasional inconsistent crashing (memory issue perhaps)
    sometimes, the global rate gets stuck. I have no idea where or why this happens. Seems to happen more often with active files.
        probably fixable, but none of my print statements have been useful at indicating the timing or cause of this issue. sorry.
        
    luminosity has a weird thing where it doesn't fill a bin every 5 seconds (or whatever the update rate is)
        probably fixable, but I didn't have time. sorry.

    the argument for beammode for some reason only  gets the first word (e.g. stable in stable beams)
        current remedy: checks on beammode in task.setBeamParam are if [arg] in [beam mode]
