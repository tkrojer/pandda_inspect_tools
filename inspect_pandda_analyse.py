# plugin for COOT to inspect and model pandda.analyse results
#
# Copyright (c) 2022, Tobias Krojer, MAX IV Laboratory
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import glob
import sys
import shutil

import gtk
import coot
import __main__

import csv


class inspect_gui(object):

    def __init__(self):

        self.index = -1
        self.Todo = []
        self.mol_dict = {
            'protein': None,
            'emap': None,
            'ligand': None
            }

        self.panddaDir = None
        self.eventCSV = None
        self.reset_params()

        self.ligand_confidence_button_labels = [
            [0, 'unassigned'],
            [1, 'no ligand bound'],
            [2, 'unknown ligand'],
            [3, 'low confidence'],
            [4, 'high confidence']
        ]

        self.selection_criteria = [
            'show all events',
            'show not viewed events',
            'show unassigned',
            'show no ligands bound',
            'show unknown ligands',
            'show low confidence ligands',
            'show high confidence ligands'
        ]

        self.selected_selection_criterion = None


    def startGUI(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(10)
        self.window.set_default_size(400, 600)
        self.window.set_title("inspect")
        self.vbox = gtk.VBox()  # this is the main container

        frame = gtk.Frame(label='PanDDA folder')
        hbox = gtk.HBox()
        select_pandda_folder_button = gtk.Button(label="select pandda directory")
        hbox.add(select_pandda_folder_button)
        select_pandda_folder_button.connect("clicked", self.select_pandda_folder)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='Event selection')
        hbox = gtk.HBox()
        self.select_events_combobox = gtk.combo_box_new_text()
        #        self.select_events_combobox.connect("changed", self.set_selection_mode)
        for citeria in self.selection_criteria:
            self.select_events_combobox.append_text(citeria)
        hbox.pack_start(self.select_events_combobox)
        select_events_button = gtk.Button(label="Go")
        select_events_button.connect("clicked", self.select_events)
        hbox.pack_start(select_events_button)
        frame.add(hbox)
        self.vbox.add(frame)

        outer_frame = gtk.Frame()
        hbox = gtk.HBox()

        table = gtk.Table(7, 2, False)

        frame = gtk.Frame()
        frame.add(gtk.Label('Crystal'))
        table.attach(frame, 0, 1, 0, 1)
        frame = gtk.Frame()
        self.xtal_label = gtk.Label('')
        frame.add(self.xtal_label)
        table.attach(frame, 1, 2, 0, 1)

        frame = gtk.Frame()
        frame.add(gtk.Label('Resolution'))
        table.attach(frame, 0, 1, 1, 2)
        frame = gtk.Frame()
        self.resolution_label = gtk.Label('')
        frame.add(self.resolution_label)
        table.attach(frame, 1, 2, 1, 2)

        frame = gtk.Frame()
        frame.add(gtk.Label('Rwork'))
        table.attach(frame, 0, 1, 2, 3)
        frame = gtk.Frame()
        self.r_work_label = gtk.Label('')
        frame.add(self.r_work_label)
        table.attach(frame, 1, 2, 2, 3)

        frame = gtk.Frame()
        frame.add(gtk.Label('Rfree'))
        table.attach(frame, 0, 1, 3, 4)
        frame = gtk.Frame()
        self.r_free_label = gtk.Label('')
        frame.add(self.r_free_label)
        table.attach(frame, 1, 2, 3, 4)

        frame = gtk.Frame()
        frame.add(gtk.Label('Event'))
        table.attach(frame, 0, 1, 4, 5)
        frame = gtk.Frame()
        self.event_label = gtk.Label('')
        frame.add(self.event_label)
        table.attach(frame, 1, 2, 4, 5)

        frame = gtk.Frame()
        frame.add(gtk.Label('Site'))
        table.attach(frame, 0, 1, 5, 6)
        frame = gtk.Frame()
        self.site_label = gtk.Label('')
        frame.add(self.site_label)
        table.attach(frame, 1, 2, 5, 6)

        frame = gtk.Frame()
        frame.add(gtk.Label('BDC'))
        table.attach(frame, 0, 1, 6, 7)
        frame = gtk.Frame()
        self.bdc_label = gtk.Label('')
        frame.add(self.bdc_label)
        table.attach(frame, 1, 2, 6, 7)

        outer_frame.add(table)
        hbox.add(outer_frame)
        self.vbox.add(hbox)

        frame = gtk.Frame(label='Navigator')
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        previous_event_button = gtk.Button(label="<<< Event")
        previous_event_button.connect("clicked", self.previous_event)
        hbox.pack_start(previous_event_button)
        next_event_button = gtk.Button(label="Event >>>")
        next_event_button.connect("clicked", self.next_event)
        hbox.pack_start(next_event_button)
        vbox.add(hbox)
        hbox = gtk.HBox()
        previous_site_button = gtk.Button(label="<<< Site")
        previous_site_button.connect("clicked", self.previous_site)
        hbox.pack_start(previous_site_button)
        next_site_button = gtk.Button(label="Site >>>")
        next_site_button.connect("clicked", self.next_site)
        hbox.pack_start(next_site_button)
        vbox.add(hbox)
        frame.add(vbox)
        self.vbox.add(frame)

        frame = gtk.Frame(label='Toggle Maps')
        hbox = gtk.HBox()
        toggle_emap_button = gtk.Button(label="event map")
        hbox.add(toggle_emap_button)
        toggle_emap_button.connect("clicked", self.toggle_emap)
        toggle_zmap_button = gtk.Button(label="Z-map")
        hbox.add(toggle_zmap_button)
        toggle_zmap_button.connect("clicked", self.toggle_zmap)
        toggle_x_ray_maps_button = gtk.Button(label="(2)fofc maps")
        hbox.add(toggle_x_ray_maps_button)
        toggle_x_ray_maps_button.connect("clicked", self.toggle_x_ray_maps)
        self.toggle_average_map_button = gtk.Button(label="average map")
        hbox.add(self.toggle_average_map_button)
        self.toggle_average_map_button.connect("clicked", self.toggle_average_map)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='Ligand Modeling')
        hbox = gtk.HBox()
        place_ligand_here_button = gtk.Button(label="Place Ligand here")
        place_ligand_here_button.connect("clicked", self.place_ligand_here)
        hbox.add(place_ligand_here_button)
        merge_ligand_button = gtk.Button(label="Merge Ligand")
        merge_ligand_button.connect("clicked", self.merge_ligand_into_protein)
        hbox.add(merge_ligand_button)
        reset_to_unfitted_button = gtk.Button(label="Revert to unfitted")
        reset_to_unfitted_button.connect("clicked", self.reset_to_unfitted)
        hbox.add(reset_to_unfitted_button)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='Annotation')
        vbox = gtk.VBox()
        self.ligand_confidence_button_list = []
        for n, item in enumerate(self.ligand_confidence_button_labels):
            if n == 0:
                button = gtk.RadioButton(None, item[1])
            else:
                button = gtk.RadioButton(button, item[1])
            button.connect("toggled", self.set_ligand_confidence, item[1])
            self.ligand_confidence_button_list.append(button)
            vbox.add(button)
            button.show()
        frame.add(vbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='Save')
        hbox = gtk.HBox()
        self.save_next_button = gtk.Button(label="Save Model")
        hbox.add(self.save_next_button)
        self.save_next_button.connect("clicked", self.save_next)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        self.window.add(self.vbox)
        self.window.show_all()

    def save_pandda_inspect_events_csv_file(self):
        with open(os.path.join(self.analysis_folder, 'pandda_inspect_events.csv'), 'w') as csvfile:
            print('INSPECT - INFO: updating {0!s}'.format(
                os.path.join(self.analysis_folder, 'pandda_inspect_events.csv')))
            writer = csv.writer(csvfile)
            writer.writerows(self.elist)

    def set_ligand_confidence(self, widget, data=None):
        if widget.get_active():
            self.elist[self.index][self.ligand_confidence_index] = data
            self.save_pandda_inspect_events_csv_file()
#            with open(os.path.join(self.analysis_folder, 'pandda_inspect_events.csv'), 'w') as csvfile:
#                print('INSPECT - INFO: updating {0!s}'.format(
#                    os.path.join(self.analysis_folder, 'pandda_inspect_events.csv')))
#                writer = csv.writer(csvfile)
#                writer.writerows(self.elist)

    def save_event_as_viewed(self):
        self.elist[self.index][self.viewed_index] = 'True'
        self.save_pandda_inspect_events_csv_file()

    def set_ligand_confidence_button(self):
        foundItem = False
        for item in self.ligand_confidence_button_labels:
            if item[1] == self.ligand_confidence:
                self.ligand_confidence_button_list[item[0]].set_active(True)
                foundItem = True
                break
        if not foundItem:
            self.ligand_confidence_button_list[0].set_active(True)

    def select_pandda_folder(self, widget):
        dlg = gtk.FileChooserDialog("Open..", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = dlg.run()
        self.panddaDir = dlg.get_filename()

        self.analysis_folder = ''
        if os.path.isdir(os.path.join(self.panddaDir, 'results')):
            self.analysis_folder = os.path.join(self.panddaDir, 'results')
        elif os.path.isdir(os.path.join(self.panddaDir, 'analyses')):
            self.analysis_folder = os.path.join(self.panddaDir, 'analyses')
        elif os.path.isdir(os.path.join(self.panddaDir, 'analysis')):
            self.analysis_folder = os.path.join(self.panddaDir, 'analysis')

        self.eventCSV = os.path.realpath(os.path.join(self.analysis_folder, 'pandda_inspect_events.csv'))
        self.siteCSV = os.path.realpath(os.path.join(self.analysis_folder, 'pandda_inspect_sites.csv'))

        if not os.path.isfile(self.eventCSV):
            analyse_csv = self.eventCSV.replace('pandda_inspect_events.csv', 'pandda_analyse_events.csv')
            if not os.path.isfile(analyse_csv):
                print('INSPECT - ERROR: something went wrong; cannot find {0!s}'.format(analyse_csv))
                return
            else:
                self.initialize_inspect_events_csv_file(analyse_csv)

        if not os.path.isfile(self.eventCSV):
            print('INSPECT - ERROR: something went wrong; cannot find {0!s}'.format(self.eventCSV))
            return

        if not os.path.isfile(self.siteCSV):
            analyse_csv = self.siteCSV.replace('pandda_inspect_sites.csv', 'pandda_analyse_sites.csv')
            if not os.path.isfile(analyse_csv):
                print('INSPECT - ERROR: something went wrong; cannot find {0!s}'.format(analyse_csv))
                return
            else:
                self.initialize_inspect_sites_csv_file(analyse_csv)

        if not os.path.isfile(self.siteCSV):
            print('INSPECT - ERROR: something went wrong; cannot find {0!s}'.format(self.siteCSV))
            return

        dlg.destroy()
        self.parsepanddaDir()

    def get_pdb(self, missing_files):
        if os.path.isfile(
                os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures',
                             '{0!s}-pandda-model.pdb'.format(self.xtal))):
            pdb = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures',
                             '{0!s}-pandda-model.pdb'.format(self.xtal))
            print('INSPECT - INFO: found pdb file in modelled_structures folder: {0!s}'.format(pdb))
        elif os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                         '{0!s}-pandda-input.pdb'.format(self.xtal))):
            pdb = os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                               '{0!s}-pandda-input.pdb'.format(self.xtal))
            print('INSPECT - INFO: found pdb file: {0!s}'.format(pdb))
        else:
            print('INSPECT - ERROR: did not find pdb file')
            missing_files = True
        return pdb, missing_files

    def load_pdb(self):
        coot.set_nomenclature_errors_on_read("ignore")
        imol = coot.handle_read_draw_molecule_with_recentre(self.pdb, 0)
        self.mol_dict['protein'] = imol
        coot.set_show_symmetry_master(1)  # master switch to show symmetry molecules
        coot.set_show_symmetry_molecule(imol, 1)  # show symm for model

    def get_emap(self, missing_files):
        emap = ''
        new_pandda_output = False
        event_number = (3 - len(str(self.event))) * '0' + str(self.event)
        if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                '{0!s}-event_{1!s}_1-BDC_{2!s}_map.native.mtz'.format(self.xtal, self.event, self.bdc))):
            emap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                '{0!s}-event_{1!s}_1-BDC_{2!s}_map.native.mtz'.format(self.xtal, self.event, self.bdc))
            print('INSPECT - INFO: found event map: {0!s}'.format(emap))
        elif os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                '{0!s}-pandda-output-event-{1!s}.mtz'.format(self.xtal, event_number))):
            emap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                '{0!s}-pandda-output-event-{1!s}.mtz'.format(self.xtal, event_number))
            print('INSPECT - INFO: found event map: {0!s}'.format(emap))
            new_pandda_output = True
        else:
            emap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                '{0!s}-event_{1!s}_1-BDC_{2!s}_map.native.mtz'.format(self.xtal, self.event, self.bdc))
            print('INSPECT - ERROR: cannot find event map {0!s}'.format(emap))
            print('INSPECT - REMINDER: make sure that all CCP4 maps are converted into MTZ format!')
            missing_files = True
        print('INSPECT - INFO: new pandda file names: {0!s}'.format(new_pandda_output))
        return emap, new_pandda_output, missing_files

    def load_emap(self):
        if self.new_pandda_output:
            imol = coot.map_from_mtz_by_calc_phases(self.emap, "FEVENT", "PHEVENT", self.mol_dict['protein'])
            self.mol_dict['emap'] = imol
        else:
            imol = coot.auto_read_make_and_draw_maps(self.emap)
            self.mol_dict['emap'] = imol[0]
        coot.set_colour_map_rotation_on_read_pdb(0)
        coot.set_last_map_colour(0, 0, 1)
        self.show_emap = 1
        # event map contour level:
        # if you divide it by (1-bdc) you get the contour level in RMSD.
        # for 1-bdc = 0.3, then contouring at 0.3 is 1 RMSD, 0.6 is 2 RMSD, etc.
        # note self.bdc is actually 1-bdc
        # emap_level = 1.0 - float(self.bdc)
        coot.set_contour_level_in_sigma(self.mol_dict['emap'], float(self.bdc)*2)

    def get_zmap(self, missing_files):
        zmap = ''
        if os.path.isfile(
                os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-z_map.native.mtz'.format(self.xtal))):
            zmap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-z_map.native.mtz'.format(self.xtal))
            print('INSPECT - INFO: found z-map map: {0!s}'.format(zmap))
        elif os.path.isfile(
                os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-pandda-output.mtz'.format(self.xtal))):
            zmap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-pandda-output.mtz'.format(self.xtal))
            print('INSPECT - INFO: found z-map map: {0!s}'.format(zmap))
        else:
            print('INSPECT - ERROR: cannot find z-map!!!')
            missing_files = True
        return zmap, missing_files

    def load_zmap(self):
        coot.set_default_initial_contour_level_for_difference_map(3)
        if self.new_pandda_output:
            imol = coot.map_from_mtz_by_calc_phases(self.zmap, "FZVALUES", "PHZVALUES", self.mol_dict['protein'])
            self.mol_dict['zmap'] = imol
            coot.set_map_is_difference_map(imol, True)
        else:
            imol = coot.auto_read_make_and_draw_maps(self.zmap)
            self.mol_dict['zmap'] = imol[0]
            coot.set_contour_level_in_sigma(self.mol_dict['zmap'], 3)
#        coot.set_contour_level_in_sigma(imol[0], 3)
        self.show_zmap = 1

    def get_xraymap(self, missing_files):
        xraymap = ''
        if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets',
                                       self.xtal, '{0!s}-pandda-input.mtz'.format(self.xtal))):
            xraymap = os.path.join(self.panddaDir, 'processed_datasets',
                                   self.xtal, '{0!s}-pandda-input.mtz'.format(self.xtal))
            print('INSPECT - INFO: found xray map: {0!s}'.format(xraymap))
        else:
            print('INSPECT - ERROR: did not find xray map')
            missing_files = True
        return xraymap, missing_files

    def load_xraymap(self):
        imol = coot.auto_read_make_and_draw_maps(self.xraymap)
        self.mol_dict['xraymap'] = imol
        coot.set_colour_map_rotation_on_read_pdb(0)
        __main__.toggle_display_map(self.mol_dict['xraymap'][0], self.show_xraymap)
        __main__.toggle_display_map(self.mol_dict['xraymap'][1], self.show_xraymap)
        coot.set_last_map_colour(0, 0, 1)

    def get_averagemap(self):
        averagemap = ''
        if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                       '{0!s}-ground-state-average-map.native.mtz'.format(self.xtal))):
            averagemap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                      '{0!s}-ground-state-average-map.native.mtz'.format(self.xtal))
            print('INSPECT - INFO: found average map: {0!s}'.format(averagemap))
            self.toggle_average_map_button.set_sensitive(True)
        elif os.path.isfile(
                os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-pandda-output.mtz'.format(self.xtal))):
            averagemap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-pandda-output.mtz'.format(self.xtal))
            print('INSPECT - INFO: found average map: {0!s}'.format(averagemap))
            self.toggle_average_map_button.set_sensitive(True)
        else:
            print('INSPECT - WARNING: did not find average map; disabling "average map" button')
            self.toggle_average_map_button.set_sensitive(False)
        return averagemap

    def load_averagemap(self):
        if self.new_pandda_output:
            imol = coot.map_from_mtz_by_calc_phases(self.zmap, "FGROUND", "PHGROUND", self.mol_dict['protein'])
            self.mol_dict['averagemap'] = imol
        else:
            imol = coot.auto_read_make_and_draw_maps(self.averagemap)
            self.mol_dict['averagemap'] = imol[0]
        coot.set_colour_map_rotation_on_read_pdb(0)
        __main__.toggle_display_map(self.mol_dict['averagemap'], self.show_averagemap)
        coot.set_last_map_colour(0, 0, 1)

    def get_ligcif(self):
        foundCIF = False
        ligcif = ''
        if self.event:
            if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal, self.event, 'rhofit', 'best.cif')):
                ligcif = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, self.event, 'rhofit', 'best.cif')
                print('INSPECT - INFO: found ligand cif file: {0!s}'.format(ligcif))
                foundCIF = True
        if not foundCIF:
            for l in glob.glob(os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'ligand_files', '*cif')):
                ligcif = l
                print('INSPECT - INFO: found ligand cif file: {0!s}'.format(ligcif))
                foundCIF = True
                break
        if not foundCIF:
            print('INSPECT - WARNING: did not find ligand cif file! Check if this folder contains any files: {0!s}'.format(
                os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'ligand_files')))
        return ligcif

    def load_ligcif(self):
        if os.path.isfile(self.ligcif):
            coot.read_cif_dictionary(os.path.join(self.ligcif))
            imol = coot.handle_read_draw_molecule_with_recentre(self.ligcif.replace('.cif','.pdb'), 0)
#            imol = coot.handle_read_draw_molecule_with_recentre(self.ligcif.replace('.cif', '.pdb'), 1)
            self.mol_dict['ligand'] = imol
            coot.seqnum_from_serial_number(imol, "X", 0)
            coot.set_b_factor_residue_range(imol, "X", 1, 1, 20.00)
            coot.set_occupancy_residue_range(imol, "X", 1, 1, float(self.bdc)*2)

    def recentre_on_event(self):
        coot.set_rotation_centre(self.x, self.y, self.z)

    def reset_params(self):
        self.xtal = None
        self.event = None
        self.bdc = None
        self.site = None
        self.pdb = None
        self.emap = None
        self.new_pandda_output = False
        self.zmap = None
        self.xraymap = None
        self.averagemap = None
        self.ligcif = None
        self.x = None
        self.y = None
        self.z = None
        self.resolution = None
        self.r_free = None
        self.r_work = None
        self.ligand_confidence = None

    def update_params(self):
        missing_files = False
        self.xtal = self.elist[self.index][self.xtal_index]
        self.event = self.elist[self.index][self.event_index]
        self.bdc = self.elist[self.index][self.bdc_index]
        self.site = self.elist[self.index][self.site_index]
        print('INSPECT - INFO: checking if files exist for  {0!s}, event: {1!s}, site: {2!s}'.format(self.xtal, self.event,
                                                                                          self.site))
        self.pdb, missing_files = self.get_pdb(missing_files)
        self.emap, self.new_pandda_output, missing_files = self.get_emap(missing_files)
        self.zmap, missing_files = self.get_zmap(missing_files)
        self.xraymap, missing_files = self.get_xraymap(missing_files)
        self.averagemap = self.get_averagemap()
        self.ligcif = self.get_ligcif()
        self.x = float(self.elist[self.index][self.x_index])
        self.y = float(self.elist[self.index][self.y_index])
        self.z = float(self.elist[self.index][self.z_index])
        print('INSPECT - INFO: event coordinates -> x = {0!s}, y = {1!s}, z = {2!s}'.format(self.x, self.y, self.z))
        self.resolution = self.elist[self.index][self.resolution_index]
        self.r_free = self.elist[self.index][self.r_free_index]
        self.r_work = self.elist[self.index][self.r_work_index]
        self.ligand_confidence = self.elist[self.index][self.ligand_confidence_index]
        return missing_files

    def update_labels(self):
        self.xtal_label.set_label(self.xtal)
        self.resolution_label.set_label(self.resolution)
        self.r_free_label.set_label(self.r_free)
        self.r_work_label.set_label(self.r_work)
        self.event_label.set_label(self.event)
        self.site_label.set_label(self.site)
        self.bdc_label.set_label(self.bdc)

    def current_sample_matches_selection_criteria(self):
        show_event = False
        if self.selected_selection_criterion == "show all events":
            show_event = True
        elif self.selected_selection_criterion == "show no ligands bound":
            if "no ligand bound" in self.ligand_confidence:
                show_event = True
        elif self.selected_selection_criterion == "show unknown ligands":
            if "unknown ligand" in self.ligand_confidence:
                show_event = True
        elif self.selected_selection_criterion == "show low confidence ligands":
            if "low confidence" in self.ligand_confidence:
                show_event = True
        elif self.selected_selection_criterion == "show high confidence ligands":
            if "high confidence" in self.ligand_confidence:
                show_event = True
        elif self.selected_selection_criterion == 'show not viewed events':
            if not 'True' in self.elist[self.index][self.viewed_index]:
                show_event = True
        return show_event


    def RefreshData(self):

        self.reset_params()

        if len(__main__.molecule_number_list()) > 0:
            for item in __main__.molecule_number_list():
                coot.close_molecule(item)

        self.mol_dict = {
            'pdb': None,
            'emap': None,
            'zmap': None,
            'ligand': None,
            'xraymap': None,
            'averagemap': None
            }

        self.show_emap = 0
        self.show_zmap = 0
        self.show_xraymap = 0
        self.show_averagemap = 0

        if self.index < 1:
            self.index = 1
        if self.index > len(self.elist) - 1:
            self.index = len(self.elist) - 1
            print('INSPECT - WARNING: you reached the end of available events!')
            return None

        missing_files = self.update_params()

        # check if event fits selection criteria
        if self.current_sample_matches_selection_criteria() and not missing_files:
            print('INSPECT - INFO: loading files for {0!s}, event: {1!s}, site: {2!s}'.format(self.xtal, self.event, self.site))
            self.set_ligand_confidence_button()
            self.update_labels()
            self.recentre_on_event()
            self.load_ligcif()
            self.load_pdb()
            self.load_emap()
            self.load_zmap()
            self.load_xraymap()
            if self.averagemap:
                self.load_averagemap()
        elif self.current_sample_matches_selection_criteria() and missing_files:
            print('INSPECT - ERROR: essential files could not be found, check messages above; skipping...')
            self.change_event(1)
        else:
            print('INSPECT - WARNING: {0!s}, event: {1!s}, site: {2!s} does not match selection criteria; skipping'.format(self.xtal, self.event, self.site))
            self.change_event(1)


    def place_ligand_here(self, widget):
        print('INSPECT - INFO: moving ligand to pointer')
        print('INSPECT - INFO: LIGAND: ', self.mol_dict['ligand'])
        __main__.move_molecule_here(self.mol_dict['ligand'])

    def merge_ligand_into_protein(self, widget):
        print('INSPECT - INFO: merge ligand into protein structure')
        # merge_molecules(list(imols), imol) e.g. merge_molecules([1],0)
        coot.merge_molecules_py([self.mol_dict['ligand']], self.mol_dict['protein'])
        print('INSPECT - INFO: removing ligand from molecule list')
        coot.close_molecule(self.mol_dict['ligand'])

    def reset_to_unfitted(self, widget):
        for imol in __main__.molecule_number_list():
            if 'pandda-model.pdb' in coot.molecule_name(imol):
                self.pdb = os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                        '{0!s}-pandda-input.pdb'.format(self.xtal))
                coot.close_molecule(imol)
                self.load_pdb()
                break

    def check_if_modelled_structures_folder_exists(self):
        modelled_structures = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures')
        if not os.path.isdir(os.path.join(modelled_structures)):
            print('INSPECT - INFO: creating folder {0!s}'.format(modelled_structures))
            os.mkdir(modelled_structures)

    def save_next(self, widget):
        self.check_if_modelled_structures_folder_exists()
        if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                       'modelled_structures', 'fitted-v0001.pdb')):
            n = []
            for p in sorted(glob.glob(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                                   'modelled_structures', 'fitted-v*.pdb'))):
                n.append(int(p[p.rfind('fitted-v')+8:].replace('.pdb','')))
                new = 'fitted-v' + (4-len(str(max(n)+1))) * '0' + str(max(n)+1) + '.pdb'
        else:
                new = 'fitted-v0001.pdb'
        coot.write_pdb_file(self.mol_dict['protein'], os.path.join(
                    self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures', new))
        if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                       'modelled_structures', '{0!s}-pandda-model.pdb'.format(self.xtal))):
            os.remove(os.path.join(self.panddaDir,'processed_datasets', self.xtal,
                                   'modelled_structures', '{0!s}-pandda-model.pdb'.format(self.xtal)))
        os.chdir(os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures'))
        if os.name == 'nt':
            os.popen('copy {0!s} {1!s}-pandda-model.pdb'.format(new, self.xtal))
        else:
            os.symlink(new, '{0!s}-pandda-model.pdb'.format(self.xtal))

    def select_events(self, widget):
        self.selected_selection_criterion = self.select_events_combobox.get_active_text()
        print("INSPECT - INFO: you selected to {0!s}".format(self.selected_selection_criterion))
        self.index = -1

    def previous_event(self, widget):
        self.change_event(-1)

    def next_event(self, widget):
        self.save_event_as_viewed()
        self.change_event(1)

    def previous_site(self, widget):
        self.change_site(-1)

    def next_site(self, widget):
        self.change_site(1)

    def change_site(self, n):
        current_site = int(self.site)
        new_site = current_site + n
        index_increment = 0
        for i, item in enumerate(self.elist):
            if item[11] == str(new_site):
                index_increment = i - self.index
                break
        self.change_event(index_increment)

    def change_event(self, n):
        self.index += n
        self.RefreshData()


    def make_secure_copy_of_original_csv(self, csv_file):
        csv_original = csv_file + '.original'
        if not os.path.isfile(csv_original):
            print('INSPECT - INFO: creating backup file of {0!s}'.format(csv_file))
            shutil.copy(csv_file, csv_original)


    def initialize_inspect_events_csv_file(self, analyse_csv):
        self.make_secure_copy_of_original_csv(analyse_csv)
        r = csv.reader(open(analyse_csv))
        l = list(r)
        for i, line in enumerate(l):
            if i == 0:
                l[i].extend(['Interesting','Ligand Placed','Ligand Confidence','Comment','Viewed'])
            else:
                l[i].extend(['False', 'False', 'Low', 'None', 'False'])
        with open(os.path.join(self.analysis_folder,'pandda_inspect_events.csv'), 'w') as f:
            writer = csv.writer(f)
            writer.writerows(l)


    def initialize_inspect_sites_csv_file(self, analyse_csv):
        self.make_secure_copy_of_original_csv(analyse_csv)
        r = csv.reader(open(analyse_csv))
        l = list(r)
        for i, line in enumerate(l):
            if i == 0:
                l[i].extend(['Name','Comment'])
            else:
                l[i].extend(['None', 'None'])
        with open(os.path.join(self.analysis_folder,'pandda_inspect_sites.csv'), 'w') as f:
            writer = csv.writer(f)
            writer.writerows(l)

    def parsepanddaDir(self):
        print("INSPECT - INFO: reading {0!s}".format(self.eventCSV))
        r = csv.reader(open(self.eventCSV))
        self.elist = list(r)

        print("INSPECT - INFO: reading {0!s}".format(self.siteCSV))
        r = csv.reader(open(self.siteCSV))
        self.slist = list(r)

        print("INSPECT - INFO: getting header fields from {0!s}".format(self.eventCSV))
        for n, item in enumerate(self.elist[0]): # number of columns at the end can differ
            if item == 'dtag':
                self.xtal_index = n
            if item == 'Ligand Confidence':
                self.ligand_confidence_index = n
            if item == 'event_num' or item == 'event_idx':
                self.event_index = n
            if item == 'site_num' or item == 'site_idx':
                self.site_index = n
            if item == 'bdc' or item == '1-BDC':
                self.bdc_index = n
            if item == 'x':
                self.x_index = n
            if item == 'y':
                self.y_index = n
            if item == 'z':
                self.z_index = n
            if item == 'analysed_resolution' or item == 'high_resolution':
                self.resolution_index = n
            if item == 'r_work':
                self.r_work_index = n
            if item == 'r_free':
                self.r_free_index = n
            if item == 'Viewed':
                self.viewed_index = n
        self.show_content_of_event_csv_file()

    def show_content_of_event_csv_file(self):
        print("INSPECT - INFO: showing contents of {0!s}:".format(self.eventCSV))
        for n,i in enumerate(self.elist):
            if n == 0:
                continue
            x = round(float(self.elist[n][self.x_index]), 1)
            y = round(float(self.elist[n][self.y_index]), 1)
            z = round(float(self.elist[n][self.z_index]), 1)
            info = (
                'INSPECT - INFO: '
                ' xtal: {0!s}'.format(self.elist[n][self.xtal_index]) +
                ' - event/site: {0!s}/{1!s}'.format(self.elist[n][self.event_index],self.elist[n][self.site_index]) +
                ' - BDC: {0!s}'.format(self.elist[n][self.bdc_index]) +
                ' - x,y,z: {0!s},{1!s},{2!s}'.format(x, y, z) +
                ' - Resolution: {0!s}'.format(self.elist[n][self.resolution_index]) +
                ' - Rwork/Rfree: {0!s}/{1!s}'.format(self.elist[n][self.r_work_index],self.elist[n][self.r_free_index]) +
                ' - viewed: {0!s}'.format(self.elist[n][self.viewed_index]) +
                ' - ligand confidence: {0!s}'.format(self.elist[n][self.ligand_confidence_index])
            )
            print(info)

    def toggle_emap(self, widget):
        if self.mol_dict['emap'] is not None:
            if self.show_emap == 0:
                self.show_emap = 1
            else:
                self.show_emap = 0
            __main__.toggle_display_map(self.mol_dict['emap'], self.show_emap)

    def toggle_zmap(self, widget):
        if self.mol_dict['zmap'] is not None:
            if self.show_zmap == 0:
                self.show_zmap = 1
            else:
                self.show_zmap = 0
            __main__.toggle_display_map(self.mol_dict['zmap'], self.show_zmap)

    def toggle_x_ray_maps(self, widget):
        if self.mol_dict['xraymap'] is not None:
            if self.show_xraymap == 0:
                self.show_xraymap = 1
            else:
                self.show_xraymap = 0
            __main__.toggle_display_map(self.mol_dict['xraymap'][0], self.show_xraymap)
            __main__.toggle_display_map(self.mol_dict['xraymap'][1], self.show_xraymap)

    def toggle_average_map(self, widget):
        if self.mol_dict['averagemap'] is not None:
            if self.show_averagemap == 0:
                self.show_averagemap = 1
            else:
                self.show_averagemap = 0
            __main__.toggle_display_map(self.mol_dict['averagemap'], self.show_averagemap)

    def CANCEL(self, widget):
        self.window.destroy()

if __name__ == '__main__':
    inspect_gui().startGUI()
