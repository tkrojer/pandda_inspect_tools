# pandda_inspect_tools

## Description

This repository contains several programs for manipulation and inspection of results from pandda.analyse. The scripts do essentially the same as the tools provided by the [PanDDA suite](https://pandda.bitbucket.io/#), but they are compatible the latest version of CCP4 and the inspect plugin for COOT also works on Windows operating systems. The scripts work for the original PanDDA program, as well as for the more recent [PanDDA2](https://github.com/ConorFWild/pandda_2_gemmi). The following scripts are included in the repository:

- convert_event_map_to_mtz.py
- inspect_pandda_analyse.py
- export_pandda_models.py


## convert_event_map_to_mtz.py

pandda.analyse creates event, average and z-maps in CCP4 map format and convert_event_map_to_mtz.py is a python script to convert the maps into MTZ files. You need to run this script if you want to explore results from pandda.analyse with inspect_pandda_analyse.py because, in contrast to pandda.inspect, it only reads maps as MTZ files and then uses the auto-read function in COOT to convert them into (difference) maps.

### <span style="color:red">**Important**</span>
<span style="color:red">
It seems that newer versions of COOT (0.9.6) occasionally do not display maps from PanDDA around the protein molecule. If this is the case for your maps, then the conversion to MTZ format does not help and you need to swap the axis order of every map before they are correctly displayed. You can use the "-c" option to show the axis order of the current maps and then use the "-a" option to change the axis order. Most of the time, -a xyz will do the job (see examples below).</br>      </br>
Another indication for problems with the axis order of the maps is when you get the following error message:

```
ERROR: grid size is not compatible with space group.
```

Do the same as described above, i.e. show the current axis order, then try a permutaton thereof (the option "-a xyz" will do most of the time).* 

#### <span style="color:red">**Notes:**</span>
- the script will never touch the original maps, i.e. you can run it as often as you want and it will not case any harm!
- The script will only show you the axis order of the original maps, not of the maps converted to MTZ format
</span> 

### Usage

```
# convert maps
ccp4-python convert_event_map_to_mtz.py -p /data/user/pandda

# show current axis order
ccp4-python convert_event_map_to_mtz.py -p /data/user/pandda -c

# convert maps and change axis order
ccp4-python convert_event_map_to_mtz.py -p /data/user/pandda -a xyz

# convert maps, change axis order and overwrite existing MTZ files
ccp4-python convert_event_map_to_mtz.py -p /data/user/pandda -a xyz -o
```



## inspect_pandda_analyse.py

inspect_pandda_analyse.py is a python plugin for COOT that enables inspection of [PanDDA](https://pandda.bitbucket.io/#) event maps and modelling of ligands. It is a minimalistic version of pandda.inspect, but it works on Windows, MAC and Linux and with the latest version of CCP4/ COOT. There is however one important difference to the original pandda.inspect program: inspect_pandda_analyse.py only reads MTZ files, not the CCP4 maps produced by pandda.analyse! This means that you first need to convert the maps with convert_event_map_to_mtz.py before you can view them.

### Usage

The COOT plugin can either be started from the command line by typing
```
coot --script inspect_pandda_analyse.py
```
or from the COOT gui, by selecting
```
Calculate -> Run Script...
```
Use the file selection dialog to locate the script, then press Open. In addition to the usual COOT window, a separate window for the inspct interface should appear.  </br> </br>

Once the interface appears, do the following:

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide1.png)

Click on "select pandda directory" and use the folder dialog to select the respective directory:

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide2.png)

Nothing much will happen (though at some point in the future I will try to make the interface a bit more chatty). Use the "event selection" dropdown (1) to select which events you want to see, then press "Go" (2). You can use the buttons in the "Toggle maps" secton to turn different kinds of maps on and off.</br>
Note: you can use the "Annotation" box at the bottom of the panel to annotate events. Every annotation will be stored in pandda_inspect_events.csv and you can use the "event selection" dropdown to only look at subsets.

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide3.png)

Again, not much has happened after you pressed "Go". Now, use the "Event" and "Site" arrows in the "Navigator" section to go through your events. 
Note: the interface goes through the events/ sites in the same order as in the pandda_inspect_events.csv file.

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide4.png)

For ligand modelling, press "Place Ligand here" (1) then fit the ligand to the density. When you are done, press "Merge Ligand" (2). The ligand molecule will disappear but will immediately reappear once you move the scene a bit. Finallyt, press "Revert to unfitted" in case you want to start all over again.</br>
Note:
- the 
- inspect_pandda_analyse.py, just like pandda.inspect, looks for ligand PDB and CIF files in the XXX folder

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide5.png)

Finally, you can annotate the event with the given options (1). All annotattion are stored in pandda_inspect_events.csv and the "event selection" dropdown can be used to only look at subsets of the pandda results. The last thing to do is to press "Save Model", then a copy of the model on the screen will be saved in the "modelled_structures" folder of the respective dataset directory.

Note:
- the models is saved as a single conformer model and the placed ligand gets a occupancy value assigned that is twice the BDC value. This is exactly the same as in pandda.inspect. Creatiion of an ensemble model only happens at the export stage.

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide6.png)


## export_pandda_models.py

Script for exporting models built with pandda.inspect or inspect_pandda_analyse.py into a new target directory. The script does similar things like the original pandda.export, but there are a few differences:

- It copies MTZ files with map coeffcients (as generated by convert_event_map_to_mtz.py) into the target directory, but no CCP4 maps.
- Generation of ensemble models is optional! The default is to export models as single conformer models. You need to use the -n option for the script to first generate an ensemble model with giant.merge_conformations and then to copy the resulting PDB file into the target directory.
- Default is to just analyse the contents pandda directory, i.e. you need to set the -e option to do the actual export.
- Finally, please use the -h flag to get a list of all options


### Examples:

```
# show all available options ("-h")
ccp4-python export_pandda_models.py -h

# export single conformer models from pandda directory ("-p") to target directory ("-d")
ccp4-python export_pandda_models.py -p /home/tobias/pandda -d /home/tobias/refine -e

# export high-confidence ("-c") single conformer models
ccp4-python export_pandda_models.py -p /home/tobias/pandda -d /home/tobias/refine -e -c

# export low-confidence ("-l") ensemble ("-n") models
ccp4-python export_pandda_models.py -p /home/tobias/pandda -d /home/tobias/refine -e -l -n
```


## Prerequistes & Installation

Usage of the scripts does not require any complicated installation procedures, All you need to do is to either download the individual python scripts or download the entire repository (e.g. as ZIP file) and unpack it where you want to install it. This can be a local drive or a network drive. </br>

All you need is a working and reasonably up-to-date version of CCP4 (v7.1 or higher).

convert_event_map_to_mtz.py and export_pandda_models.py work for python2 and python3. They mostly use libraries that are part of most python installations. The only exception is [gemmi](https://gemmi.readthedocs.io/en/latest/#). An easy solution is to run the scripts with ccp4-python which comes with gemmi. Another convenient possibility is to use the conda package manager for gemmi installation.


Moreover, they make use of the programs, [mapdump](https://www.ccp4.ac.uk/html/mapdump.html), [mapmask](https://www.ccp4.ac.uk/html/mapmask.html) and the standalons version of [gemmi](https://gemmi.readthedocs.io/en/latest/utils.html). But no worries, you will not need to install these programs because they are part of the CCP4 suite and as long as the suite is working on your local machine, they will be availble.

