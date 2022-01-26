import os
import glob
import sys

import pygtk, gtk, pango
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

    def StartGUI(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(10)
        self.window.set_default_size(400, 600)
        self.window.set_title("inspect")
        self.vbox = gtk.VBox()  # this is the main container

        frame = gtk.Frame(label='Open')
        hbox = gtk.HBox()
        select_pandda_folder_button = gtk.Button(label="select pandda directory")
        hbox.add(select_pandda_folder_button)
        select_pandda_folder_button.connect("clicked", self.select_pandda_folder)
        frame.add(hbox)
        self.vbox.pack_start(frame)

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
        PREVbutton = gtk.Button(label="<<<")
        NEXTbutton = gtk.Button(label=">>>")
        PREVbutton.connect("clicked", self.backward)
        NEXTbutton.connect("clicked", self.forward)
        hbox = gtk.HBox()
        hbox.pack_start(PREVbutton)
        hbox.pack_start(NEXTbutton)
        frame.add(hbox)
        self.vbox.add(frame)

        frame = gtk.Frame(label='Ligand Modeling')
        hbox = gtk.HBox()
        merge_ligand_button = gtk.Button(label="Merge Ligand")
        place_ligand_here_button = gtk.Button(label="Place Ligand here")
        hbox.add(place_ligand_here_button)
        place_ligand_here_button.connect("clicked", self.place_ligand_here)
        hbox.add(merge_ligand_button)
        merge_ligand_button.connect("clicked", self.merge_ligand_into_protein)
        frame.add(hbox)
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

    def select_pandda_folder(self, widget):
        dlg = gtk.FileChooserDialog("Open..", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = dlg.run()
        self.panddaDir = dlg.get_filename()
        self.eventCSV = os.path.join(self.panddaDir,'analyses','pandda_inspect_events.csv')
        self.siteCSV = os.path.join(self.panddaDir, 'analyses', 'pandda_inspect_events.csv')

        if not os.path.isfile(os.path.join(self.panddaDir,'analyses','pandda_inspect_events.csv')):
            analyse_csv = os.path.join(self.panddaDir,'analyses','pandda_analyse_events.csv')
            if not os.path.isfile(analyse_csv):
                print('ERROR: something went wrong; cannot find {0!s}'.format(analyse_csv))
                return
            else:
                self.initialize_inspect_events_csv_file(analyse_csv)

        if not os.path.isfile(self.eventCSV):
            print('ERROR: something went wrong; cannot find {0!s}'.format(self.eventCSV))
            return

        if not os.path.isfile(os.path.join(self.panddaDir,'analyses','pandda_inspect_sites.csv')):
            analyse_csv = os.path.join(self.panddaDir,'analyses','pandda_inspect_sites.csv')
            if not os.path.isfile(analyse_csv):
                print('ERROR: something went wrong; cannot find {0!s}'.format(analyse_csv))
                return
            else:
                self.initialize_inspect_sites_csv_file(analyse_csv)

        if not os.path.isfile(self.siteCSV):
            print('ERROR: something went wrong; cannot find {0!s}'.format(self.siteCSV))
            return

        dlg.destroy()
        self.parsepanddaDir()

    def get_pdb(self):
        pdb = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-pandda-input.pdb'.format(self.xtal))
        if os.path.isfile(
                os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures',
                             '{0!s}-pandda-model.pdb'.format(self.xtal))):
            pdb = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures',
                             '{0!s}-pandda-model.pdb'.format(self.xtal))
        return pdb

    def get_emap(self):
        emap = ''
        if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                       '{0!s}-event_{1!s}_1-BDC_{2!s}_map.native.ccp4'.format(self.xtal, self.event, self.bdc))):
            emap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                       '{0!s}-event_{1!s}_1-BDC_{2!s}_map.native.ccp4'.format(self.xtal, self.event, self.bdc))
        return emap

    def get_zmap(self):
        zmap = ''
        if os.path.isfile(
                os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-z_map.native.ccp4'.format(self.xtal))):
            zmap = os.path.join(self.panddaDir, 'processed_datasets', self.xtal, '{0!s}-z_map.native.ccp4'.format(self.xtal))
        return zmap

    def get_ligcif(self):
        ligcif = ''
        for l in glob.glob(os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'ligand_files', '*cif')):
            ligcif = l
            break
        return ligcif

    def reset_params(self):
        self.xtal = None
        self.event = None
        self.bdc = None
        self.site = None
        self.pdb = None
        self.emap = None
        self.zmap = None
        self.ligcif = None
        self.x = None
        self.y = None
        self.z = None
        self.resolution = None
        self.r_free = None
        self.r_work = None

    def update_params(self):
        self.xtal = self.elist[self.index][0]
        self.event = self.elist[self.index][1]
        self.bdc = self.elist[self.index][2]
        self.site = self.elist[self.index][11]
        self.pdb = self.get_pdb()
        self.emap = self.get_emap()
        self.zmap = self.get_zmap()
        self.ligcif = self.get_ligcif()
        self.x = float(self.elist[self.index][12])
        self.y = float(self.elist[self.index][13])
        self.z = float(self.elist[self.index][14])
        self.resolution = self.elist[self.index][18]
        self.r_free = self.elist[self.index][20]
        self.r_work = self.elist[self.index][21]

    def update_labels(self):
        self.xtal_label.set_label(self.xtal)
        self.resolution_label.set_label(self.resolution)
        self.r_free_label.set_label(self.r_free)
        self.r_work_label.set_label(self.r_work)
        self.event_label.set_label(self.event)
        self.site_label.set_label(self.site)
        self.bdc_label.set_label(self.bdc)

    def RefreshData(self):

        self.reset_params()

        if len(__main__.molecule_number_list()) > 0:
            for item in __main__.molecule_number_list():
                coot.close_molecule(item)

        self.mol_dict = {
            'pdb': None,
            'emap': None,
            'ligand': None
            }

        if self.index < 1:
            self.index = 1
        if self.index > len(self.elist) - 1:
            self.index = len(self.elist) - 1

        self.update_params()

        self.update_labels()

        coot.set_nomenclature_errors_on_read("ignore")
        imol = coot.handle_read_draw_molecule_with_recentre(self.pdb, 0)
        self.mol_dict['protein'] = imol
        imol = coot.handle_read_ccp4_map(self.emap, 0)
        coot.set_colour_map_rotation_on_read_pdb(0)
        coot.set_last_map_colour(0, 0, 1)
        # event map contour level:
        # if you divide it by (1-bdc) you get the contour level in RMSD.
        # for 1-bdc = 0.3, then contouring at 0.3 is 1 RMSD, 0.6 is 2 RMSD, etc.
        emap_level = 1 - self.bdc
        coot.set_contour_level_in_sigma(imol, emap_level)
        coot.set_default_initial_contour_level_for_difference_map(3)
        imol = coot.handle_read_ccp4_map(self.zmap, 1)
        coot.set_contour_level_in_sigma(imol, 3)

        if os.path.isfile(self.ligcif):
            imol = coot.handle_read_draw_molecule_with_recentre(self.ligcif.replace('.cif','.pdb'), 0)
            self.mol_dict['ligand'] = imol
            coot.read_cif_dictionary(os.path.join(self.ligcif))

        coot.set_rotation_centre(self.x, self.y, self.z)

    def place_ligand_here(self, widget):
        print('===> moving ligand to pointer')
        print('LIGAND: ', self.mol_dict['ligand'])
        __main__.move_molecule_here(self.mol_dict['ligand'])

    def merge_ligand_into_protein(self, widget):
        print('===> merge ligand into protein structure')
        # merge_molecules(list(imols), imol) e.g. merge_molecules([1],0)
        coot.merge_molecules_py([self.mol_dict['ligand']], self.mol_dict['protein'])
        print('===> deleting ligand molecule')
        coot.close_molecule(self.mol_dict['ligand'])

    def save_next(self, widget):
        if os.path.isfile(os.path.join(self.panddaDir,'processed_datasets', self.xtal,'modelled_structures', 'fitted-v0001.pdb')):
            n = []
            for p in sorted(glob.glob(os.path.join(self.panddaDir,'processed_datasets', self.xtal,'modelled_structures', 'fitted-v*.pdb'))):
                n.append(int(p[p.rfind('fitted-v')+8:].replace('.pdb','')))
                new = 'fitted-v' + (4-len(str(max(n)+1))) * '0' + str(max(n)+1) + '.pdb'
        else:
                new = 'fitted-v0001.pdb'
        coot.write_pdb_file(self.mol_dict['protein'], os.path.join(
                    self.panddaDir,'processed_datasets', self.xtal,'modelled_structures', new))
        if os.path.isfile(os.path.join(self.panddaDir,'processed_datasets', self.xtal,'modelled_structures', '{0!s}-pandda-model.pdb'.format(self.xtal))):
            os.remove(os.path.join(self.panddaDir,'processed_datasets', self.xtal,'modelled_structures', '{0!s}-pandda-model.pdb'.format(self.xtal)))
        os.chdir(os.path.join(self.panddaDir,'processed_datasets', self.xtal,'modelled_structures'))
        if os.name == 'nt':
            os.popen('copy {0!s} {1!s}-pandda-model.pdb'.format(new, self.xtal))
        else:
            os.symlink(new, '{0!s}-pandda-model.pdb'.format(self.xtal))

    def backward(self, widget):
        self.index -= 1
        self.RefreshData()

    def forward(self, widget):
        self.index += 1
        self.RefreshData()

    def initialize_inspect_events_csv_file(self, analyse_csv):
        r = csv.reader(open(analyse_csv))
        l = list(r)
        for i, line in enumerate(l):
            if i == 0:
                l[i].extend(['Interesting','Ligand Placed','Ligand Confidence','Comment','Viewed'])
            else:
                l[i].extend(['False', 'False', 'Low', 'None', 'False'])
        with open(os.path.join(self.panddaDir,'analyses','pandda_inspect_events.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(l)

    def initialize_inspect_sites_csv_file(self, analyse_csv):
        r = csv.reader(open(analyse_csv))
        l = list(r)
        for i, line in enumerate(l):
            if i == 0:
                l[i].extend(['Name','Comment'])
            else:
                l[i].extend(['None', 'None'])
        with open(os.path.join(self.panddaDir,'analyses','pandda_inspect_sites.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(l)

    def parsepanddaDir(self):
        r = csv.reader(open(self.eventCSV))
        self.elist = list(r)

        r = csv.reader(open(self.siteCSV))
        self.slist = list(r)

    def CANCEL(self, widget):
        self.window.destroy()

if __name__ == '__main__':
    inspect_gui().StartGUI()
