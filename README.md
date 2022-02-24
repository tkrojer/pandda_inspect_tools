# pandda_inspect_tools

## Description

### convert_event_map_to_mtz.py

pandda.analyse creates event, average and z-maps in CCP4 map format and convert_event_map_to_mtz.py is a python script to convert the maps into MTZ files. The script can optionally also change the axis order of the maps, because newer versions of COOT do not display the maps correctly in certain space groups.

### inspect_pandda_analyse.py

inspect_pandda_analyse.py is a python plugin for COOT that enables inspection of [PanDDA](https://pandda.bitbucket.io/#) event maps and modelling of ligands. It is a minimalistic version of pandda.inspect, but it works on Windows, MAC and Linux and with the latest version of CCP4.

## Installation

Download the repository (e.g. as ZIP file) and unpack it where you want to install it. This can be a local drive or a network drivee.

```
pandda_inspect_tools/
├── README.md
└── inspect_pandda_analyse.py
```

## Usage

The COOT plugin can either be started from the command line by typing
```
coot --script inspect_pandda_analyse.py
```
or from the COOT gui, by selecting
```
Calculate -> Run Script...
```
Use the file selection dialog to locate the script, then press Open.  


## Missing functionalities
- annotation of events
- updating of pandda_inspect_events.csv 

