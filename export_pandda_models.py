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

import getopt
import glob
import sys
import os
import csv
from tabulate import tabulate
import gemmi


def read_inspect_event_csv_as_list(panddaDir):
    inspect_csv = os.path.join(panddaDir, 'analyses', 'pandda_inspect_events.csv')
    if not os.path.isfile(inspect_csv):
        print('ERROR: cannot find {0!s}'.format(inspect_csv))
        sys.exit(2)
    print('reading {0!s}'.format)
    r = csv.reader(open(inspect_csv))
    return list(r)


def get_ligand_confidence_index(inspect_csv):
    ligand_confidence_index = 0
    for n, item in enumerate(inspect_csv[0]):  # number of columns at the end can differ
        if item == 'Ligand Confidence':
            ligand_confidence_index = n
            break
    return ligand_confidence_index


def get_info(inspect_csv, sample_id, ligand_confidence_index, model):
    ligand_confidence_list = []
    table = []
    header = ['Event', 'Site', 'BDC', 'Ligand ID', 'Distance', 'Ligand confidence']
    for item in inspect_csv:
        if item[0] == sample_id:
            event = gemmi.Position(float(item[12]), float(item[13]), float(item[13]))
            ligand, distance = assign_modelled_ligand_to_event_coordinate(model, event)
            table.append([item[1], item[11], item[2], ligand, distance, item[ligand_confidence_index]])
            if item[ligand_confidence_index] not in ligand_confidence_list:
                ligand_confidence_list.append(item[ligand_confidence_index])
    print(tabulate(table, headers=header))
    print("\n")
    return ligand_confidence_list


def assign_modelled_ligand_to_event_coordinate(model, event):
    lig = "unknown"
    distance = "unknown"
    structure = gemmi.read_structure(model, merge_chain_parts=True)
    for mod in structure:
        for chain in mod:
            for residue in chain:
                if residue.name == 'LIG':
                    c = gemmi.Chain(chain.name)
                    c.add_residue(residue, 0)
                    distance = round(event.dist(c.calculate_center_of_mass()), 2)
#                    print(distance, event.tolist(), c.calculate_center_of_mass().tolist())
                    if distance < 10:
                        lig = residue.name + '-' + chain.name + '-' + str(residue.seqid.num)
    return lig, str(distance)


#def items_to_check():
#    number_of_modeled_structures = 0
#    number_of_structures_with_at_least_one_high_confidence_ligand = 0
#    number_of_modeled_ligands = 0
#    number_of_high_confidence_ligands = 0
#    number_of_low_confidence_ligands = 0


def run_giant_merge_conformations(sample_id):
    cmd = (
        'giant.merge_conformations '
        ' major={0!s}-pandda-input.pdb '.format(sample_id) +
        ' minor=modelled_structures/{0!s}-pandda-model.pdb '.format(sample_id) +
        ' > /dev/null'
    )
    print(cmd)

def prepare_model(panddaDir, sample_id, ensembleOnly, overwrite):
    print("--> ensemble model preparation")
    if ensembleOnly:
        os.chdir(os.path.join(panddaDir, 'processed_datasets', sample_id))
        if not os.path.isfile("multi-state-model.pdb"):
            run_giant_merge_conformations(sample_id)
        elif os.path.isfile("multi-state-model.pdb") and overwrite:
            run_giant_merge_conformations(sample_id)
        else:
            print('Warning: file exists (select -o option if you want to overwrite); skipping...')
    else:
        print("default single conformer model remains active "
              "(choose option -n if you want to export an ensemble mode; skipping...")

def files_to_delete():
    files = [
        'multi-state-model.pdb',
        'multi-state-restraints.refmac.params',
        'multi-state-restraints.phenix.params',
        'ground-state-average-map.native.mtz',
        'z_map.native.mtz',
        'pandda-model.pdb'
             ]
    return files

def prepare_destination_dir(destinationDir, sample_id, overwrite):
    print("--> destination directory preparation")
    print("checking if sample folder exisits in {0!s}".format(destinationDir))
    os.chdir(destinationDir)
    if os.path.isdir(sample_id):
        print('sample directory exists; skipping...')
    else:
        print("creating sample directory")
        os.mkdir(sample_id)
    os.chdir(sample_id)
    if overwrite:
        for f in glob.glob('event_*.native.mtz'):
            print("removing " + f)
            os.remove(f)
        for f in files_to_delete():
            os.remove(f)
            print("removing " + f)


def linking_files_to_destination_dir(destinationDir, sample_id, panddaDir, ensembleOnly, model):
    print("--> linking files to destination directory")
    os.chdir(os.path.join(destinationDir, sample_id))
    if ensembleOnly:
        if os.path.isfile(os.path.join(panddaDir, 'processed_datasets', sample_id, 'multi-state-model.pdb')):
            print('ln -s {0!s}'.format(os.path.relpath(os.path.join(panddaDir, 'processed_datasets', sample_id, 'multi-state-model.pdb'))))
        if os.path.isfile(os.path.join(panddaDir, 'processed_datasets', sample_id, 'multi-state-restraints.refmac.params')):
            print('ln -s {0!s}'.format(os.path.relpath(os.path.join(panddaDir, 'processed_datasets', sample_id, 'multi-state-restraints.refmac.params'))))
        if os.path.isfile(os.path.join(panddaDir, 'processed_datasets', sample_id, 'multi-state-restraints.phenix.params')):
            print('ln -s {0!s}'.format(os.path.relpath(os.path.join(panddaDir, 'processed_datasets', sample_id, 'multi-state-restraints.phenix.params'))))
    else:
        if os.path.isfile(model):
            print('ln -s {0!s} pandda-model.pdb'.format(os.path.relpath(model)))
    if os.path.isfile(os.path.join(panddaDir, 'processed_datasets', sample_id, "{0!s}-ground-state-average-map.native.mtz".format(sample_id))):
            print('ln -s {0!s} ground-state-average-map.native.mtz'.format(os.path.relpath(os.path.join(panddaDir, 'processed_datasets', sample_id, "{0!s}-ground-state-average-map.native.mtz".format(sample_id)))))
    if os.path.isfile(os.path.join(panddaDir, 'processed_datasets', sample_id, "{0!s}-z_map.native.mtz".format(sample_id))):
            print('ln -s {0!s} z_map.native.mtz'.format(os.path.relpath(os.path.join(panddaDir, 'processed_datasets', sample_id, "{0!s}-z_map.native.mtz".format(sample_id)))))
    for event in glob.glob(os.path.join(panddaDir, 'processed_datasets', sample_id, "{0!s}-event_*_map.native.mtz".format(sample_id))):
        filename = event[event.rfind('/')+1:]
        new_filename = filename.replace(sample_id + '-', '')
        print('ln -s {0!s} {1!s}'.format(event, new_filename))

def export_pandda_models(panddaDir, destinationDir, export, highconfidenceOnly, lowconfidenceOnly, ensembleOnly, overwrite):
    inspect_csv = read_inspect_event_csv_as_list(panddaDir)
    ligand_confidence_index = get_ligand_confidence_index(inspect_csv)
    for str in sorted(glob.glob(os.path.join(panddaDir, 'processed_datasets', '*',
                                              'modelled_structures','*-pandda-model.pdb'))):
        sample_id = str.split('/')[len(str.split('/'))-3]
        print('{0!s}:\n'.format(sample_id))
        ligand_confidence_list = get_info(inspect_csv, sample_id, ligand_confidence_index, str)

        if export:
            if highconfidenceOnly:
                if "high confidence" in ligand_confidence_list:
                    prepare_model(panddaDir, sample_id, ensembleOnly, overwrite)
                    prepare_destination_dir(destinationDir, sample_id, overwrite)
                    linking_files_to_destination_dir(destinationDir, sample_id, panddaDir, ensembleOnly, model)
            elif lowconfidenceOnly:
                if "low confidence" in ligand_confidence_list and not "high confidence" in ligand_confidence_list:
                    prepare_model(panddaDir, sample_id, ensembleOnly, overwrite)







def usage():
    usage = (
        '\n'
        'export_pandda_models.py exports structures modelled with pandda.inspect or inspect_pandda_analyse.py\n'
        'into a new destination directory. The script will create subfolders corresponding to the exported \n'
        "datasets if they don't exisit in the destination directory. Otherwise, it will just copy the files \n"
        "into the respective folders.\n"
        '\n'
        'usage:\n'
        'ccp4-python export_pandda_models.py -p <pandda_dir>\n'
        'e.g.\n'
        'ccp4-python export_pandda_models.py -p /data/user/pandda\n'
        'Default: export all structures that have a ligand modelled as ensemble model'
        '\n'
        'additional command line options:\n'
        '--export, -e\n'
        '    Export models (default is to only analyse models in pandda folder).\n'
        '--destination, -d\n'
        '    Directory where models should be exported to.\n'
        '--highconfidence, -c\n'
        '    Export only high confidence hits (as labelled in pandda_inspect_events.csv).\n'
        '--lowconfidence, -l\n'
        '    Export only low confidence hits (as labelled in pandda_inspect_events.csv).\n'
        '--ensemble, -n\n'
        '    Export models as ensample models (default is as single conformer models).\n'
        '--overwrite, -o\n'
        '    Flag to overwrite previously exported files.\n'
    )
    print(usage)

def main(argv):
    panddaDir = None
    destinationDir = None
    export = False
    highconfidenceOnly = False
    lowconfidenceOnly = False
    ensembleOnly = True
    overwrite = False

    try:
        opts, args = getopt.getopt(argv,"p:d:henclo",["panddadir=", "destinationdir=", "export", "ensemble",
                                                   "highconfidence", "lowconfidence", "overwrite"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-p", "--panddadir"):
            panddaDir = arg
        elif opt in ("-d", "--destinationdir"):
            destinationDir = arg
        elif opt in ("-e", "--export"):
            export = True
        elif opt in ("-n", "--ensemble"):
            ensembleOnly = True
        elif opt in ("-c", "--highconfidence"):
            highconfidenceOnly = True
        elif opt in ("-l", "--lowconfidence"):
            lowconfidenceOnly = True
        elif opt in ("-o", "--overwrite"):
            overwrite = True


    if os.path.isdir(panddaDir):
        export_pandda_models(panddaDir, destinationDir, export, highconfidenceOnly, lowconfidenceOnly,
                             ensembleOnly, overwrite)
    else:
        print('ERROR: pandda directory does not exist -> {0!s}'.format(panddaDir))

if __name__ == '__main__':
    main(sys.argv[1:])
