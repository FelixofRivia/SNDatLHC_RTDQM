# SND@LHCdqm
Multi-threaded Python software for the online data quality monitor of the SND@LHC experiment.

## Project Status
The project is concluded. However, it will receive updates in the future with new features. The current version can plot:
- the event rate, global or per board/station; 
- the luminosity provided by ATLAS;
- the hits per channel/board/station;
- the QDC value measured by SiPMs in each station;
- the time alignment between boards;
- 2D hit plot of an XY plane.

The produced plots are saved in a ROOT file (plots.root) and are shown in real-time locally on canvases (can be disabled), refreshed every certain number of events (depending on the beam status). 
The plots produced by the machine running the monitoring script for the SND@LHC experiment are also shown live on the web page https://sndonline.web.cern.ch/rtdqm.html (must login with a CERN account).
 


## Table of Contents
* [General Information](#general-information)
* [Usage](#usage)
* [Structure of the project](#structure-of-the-project)
* [Output](#output)
* [Dependencies](#dependencies)



## General Information
SND@LHC (Scattering and Neutrino Detector at the LHC) was designed to perform measurements with high-energy neutrinos (100 GeV to a few TeV) produced at the LHC in the pseudo-rapidity region 7.2 < η < 8.4. SND@LHC is a compact, standalone experiment located in the TI18 tunnel (480 m downstream of the ATLAS interaction point, IP1) and it allows for the identification of all three flavors of neutrino interactions with high efficiency. The SND@LHC detector consists of a hybrid system with a ∼ 830 kg target made of tungsten plates interleaved with nuclear emulsion and electronic trackers (scintillating fibers, SciFi), followed by a hadronic calorimeter and a muon identification system.

The RTDQM is a multi-threaded Python software, with a main script creating and managing threads monitoring and plotting data (using pyROOT) from different detector subsystems and luminosity provided by ATLAS. The structure is modular by design, allowing for the addition (or removal) of monitoring plots. Moreover, the structure of the detector and the DAQ boards mapping is read from a configuration file that can be easily swapped, resulting in an especially flexible tool. When a data taking run begins, the SND@LHC Online System starts the RTDQM, which is able to run independently and wait for new data to update the plots.


## Usage
This project is meant to be used on ROOT files written by the SND@LHC data acquisition program, either online or stored locally. Each file contains a ROOT tree with up to $10^6$ events. Once the run number is selected, the program will try to read through all the corresponding files (in order).


The monitor can be called using  
> user@host $  python3 monitor.py --runNumber --fileNumber --beamMode

Where:
- runNumber is an integer representing the desired run number; 
- fileNumber is the desired starting file within a run (the first one is 0);
- beamMode is a string describing the status of the beam, used to select the most appropriate plotting parameters;

To kill program, enter Ctrl+\\.

## Structure of the project
The project is divided in the following way:
- **monitor.py**:  the main script which initializes all parameters and creates threads;
- **board_mapping.json**: configuration file for the DAQ boards mapping to detector subsystems;
- **luminosity.py**: script plotting luminosity in real time provided by ATLAS (feature not available outside SND@LHC monitoring machine);
- **task.py**: script with utility functions used by threads;
- **reader.py**: loads the desired file with the event tree and loops through the events. Whenever the code runs out of events, it tries to update the file and (if more events are present) resumes where it left off. This allows the code to read an active file;
- **ratePlots.py**: file with functions used to plot event/hit rate;
- **hitPlots.py**: file with functions used to plot historgrams with hits per plane/board;
- **hitMaps.py**: file with functions used to plot the 2D (XY) spread of the hits in a plane;
- **timeAlign.py**: file with functions used to visualize the time alignement between boards;
- **valuePlots.py**: file with functions used to plot the QDC value measured by SiPMs in each station;


## Output
The title of the plots contains the last updated event number from the data file.
### Event rate
<p float="left">
  <img src="https://github.com/FelixofRivia/SND-LHCdqm/assets/67705874/e2d8411f-27c8-4b55-860d-f16eaf4650ac" width="500"/>
  <img src="https://github.com/FelixofRivia/SND-LHCdqm/assets/67705874/4be0f723-b682-4124-9e99-2313ad142c96" width="500"/>
</p>

### Luminosity

### Hits per channel/board/plane
<p float="left">
  <img src="https://github.com/FelixofRivia/SND-LHCdqm/assets/67705874/d65e3303-c76d-4031-a589-6d9fef9d848b" width="300" height="450"/>
  <img src="https://github.com/FelixofRivia/SND-LHCdqm/assets/67705874/6c6c6982-effe-4cb7-a75a-6f2d8c888242" width="500" height="400"/> 
</p>

### QDC value
<img src="https://github.com/FelixofRivia/SND-LHCdqm/assets/67705874/1a8f9f8d-d0cb-4cf2-bfb5-ae1a33dfe17f" width="600"/>

### Time alignment
<img src="https://github.com/FelixofRivia/SND-LHCdqm/assets/67705874/88dad5b3-05ee-4fee-b51d-1fb92e411757" width="600"/>

### 2D hit map
<img src="https://github.com/FelixofRivia/SND-LHCdqm/assets/67705874/39d7ab37-8f26-4469-8efb-434d01215c81" width="500"/>

## Dependencies
This project is developed in a Python 3.8 environment, using the following modules:
- ROOT
- numpy
- argparse
- threading
- os
- time
- json
- math

There are additional modules needed for plotting luminosity provided by ATLAS but this feature is available only on the SND@LHC monitoring machine:
- pydim
- fcntl
