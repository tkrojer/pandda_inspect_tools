# pandda_inspect_tools

## Description

inspect_pandda_analyse.py is a python plugin for COOT that enables inspection of [PanDDA](https://pandda.bitbucket.io/#) event maps and modelling of ligands. It is a minimalistic version of pandda.inspect, but it works on Windows, MAC and Linux and with the latest version of CCP4.

## Installation

Download the repository (e.g. as ZIP file) and unpack it where you want to install it. This can be a local drive or a network drivee.

```
pandda_inspect_tools/
├── README.md
├── inspect_pandda_analyse.py
└── lib
    └── coot_utils_XChem.py
```

## Usage

It can either be started from the command line by typing
```
coot --script inspect_pandda_analyse.py
```
or from the COOT gui, by selecting
```
Calculate -> Run Script...
```
Use the file selection dialog to locate the script, then press Open.  

```
IMPORTANT: if you use the script on Windows, you must use the COOT that comes with CCP4, but NOT WinCOOT!
```

## Missing functionalities
- annotation of events
- updating of pandda_inspect_events.csv 

