# pandda_inspect_tools

## Description

This repository contains a script for inspecting results from pandda.analyse. The script does essentially the same as the original [pandda.inspect](https://pandda.bitbucket.io/#), but it is compatible with any version of of [COOT](https://www2.mrc-lmb.cam.ac.uk/personal/pemsley/coot/) v0.9 and also works on Windows operating systems. The scripts work for the original PanDDA program, as well as for the more recent [PanDDA2](https://github.com/ConorFWild/pandda_2_gemmi):

- [inspect_pandda_analyse.py](#inspecting-results-from-pandda_analyse-and-ligand-building-in-coot)


## Inspecting results from pandda_analyse and ligand building in COOT

inspect_pandda_analyse.py is a python plugin for COOT that enables inspection of [PanDDA](https://pandda.bitbucket.io/#) event maps and modelling of ligands. It is a minimalistic version of pandda.inspect, but it works on Windows, Mac and Linux and with the latest version of CCP4/ COOT. There is however one important difference to the original pandda.inspect program: inspect_pandda_analyse.py only reads MTZ files, not the CCP4 maps produced by pandda.analyse! This means that you first need to convert the maps with convert_event_map_to_mtz.py before you can view them.

### Usage

The COOT plugin can either be started from the command line by typing
```
coot --script inspect_pandda_analyse.py
```
or from the COOT gui, by selecting
```
Calculate -> Run Script...
```
Use the file selection dialog to locate the script, then press Open. In addition to the usual COOT window, a separate window for the inspct interface should appear: 

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide1.png)

Click on "select pandda directory" and use the folder dialog to select the respective directory:

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide2.png)

Nothing much will happen (though at some point in the future I will try to make the interface a bit more chatty). Use the "event selection" dropdown (1) to select which events you want to see, then press "Go" (2). You can use the buttons in the "Toggle maps" secton to turn different kinds of maps on and off.</br>
Note: you can use the "Annotation" box at the bottom of the panel to annotate events. Every annotation will be stored in pandda_inspect_events.csv and you can use the "event selection" dropdown to only look at subsets.

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide3.png)

Again, not much has happened after you pressed "Go". Now, use the "Event" and "Site" arrows in the "Navigator" section to go through your events. 
Note: the interface goes through the events/ sites in the same order as in the pandda_inspect_events.csv file.

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide4.png)

For ligand modelling, press "Place Ligand here" (1) then fit the ligand to the density. When you are done, press "Merge Ligand" (2). The ligand molecule will disappear but will immediately reappear once you move the scene a bit. Finally, press "Revert to unfitted" in case you want to start all over again.</br>
Note:
- inspect_pandda_analyse.py, just like pandda.inspect, looks for ligand PDB and CIF files in the "ligand_files" folder of the respective dataset directory, i.e. if a ligand does not appear then this is usually a good starting point for checking if the file exisits.

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide5.png)

Finally, you can annotate the event with the given options (1). All annotations are stored in pandda_inspect_events.csv and the "event selection" dropdown can be used to only look at subsets of the pandda results. The last thing to do is to press "Save Model", then a copy of the model on the screen will be saved in the "modelled_structures" folder of the respective dataset directory.

Note:
- the model is saved as a single conformer model and the placed ligand gets an occupancy value assigned that is twice the BDC value. This is exactly the same as in pandda.inspect. Creation of an ensemble model only happens at the export stage.

![](https://github.com/tkrojer/pandda_inspect_tools/blob/main/images/Slide6.png)


