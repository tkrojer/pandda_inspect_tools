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
    table = []
    header = ['Event', 'Site', 'BDC', 'Ligand ID', 'Ligand confidence']
    for item in inspect_csv:
        if item[0] == sample_id:
            event = gemmi.Position(float(item[12]), float(item[13]), float(item[13]))
            ligand = assign_modelled_ligand_to_event_coordinate(model, event)
            table.append([item[1], item[11], item[2], ligand, item[ligand_confidence_index]])
    print(tabulate((table), headers=header))
    print("\n\n")

def assign_modelled_ligand_to_event_coordinate(model, event):
    lig = "unknown"
    structure = gemmi.read_structure(model, merge_chain_parts=True)
    for mod in structure:
        for chain in mod:
            for residue in chain:
                if residue.name == 'LIG':
                    c = gemmi.Chain(chain.name)
                    c.add_residue(residue, 0)
                    print(dir(c))
                    distance = event.dist(c.calculate_center_of_mass())
                    if distance < 5:
                        lig = residue.name + '-' + chain.name + '-' + residue.seqid.num
    return lig


def items_to_check():
    number_of_modeled_structures = 0
    number_of_structures_with_at_least_one_high_confidence_ligand = 0
    number_of_modeled_ligands = 0
    number_of_high_confidence_ligands = 0
    number_of_low_confidence_ligands = 0


def export_pandda_models(panddaDir):
    inspect_csv = read_inspect_event_csv_as_list(panddaDir)
    ligand_confidence_index = get_ligand_confidence_index(inspect_csv)
    for str in sorted(glob.glob(os.path.join(panddaDir, 'processed_datasets', '*',
                                              'modelled_structures','*-pandda-model.pdb'))):
        sample_id = str.split('/')[len(str.split('/'))-3]
        print('{0!s}:\n'.format(sample_id))
        get_info(inspect_csv, sample_id, ligand_confidence_index, str)



#        if sample_id not in sampleList:
#            print('converting maps for {0!s}'.format(sample_id))
#            sampleList.append(sample_id)
#        workDir = maps[:maps.rfind('/')]
#        os.chdir(workDir)
#        pandda_input_mtz = '{0!s}-pandda-input.mtz'.format(sample_id)
#        if os.path.isfile(pandda_input_mtz):
#            dmin = get_resolution(pandda_input_mtz)
#        else:
#            print('ERROR: {0!s} does not exist; cannot get resolution of map later; skipping...'.format(pandda_input_mtz))
#            sys.exit(2)
#        map_name = maps.split('/')[len(maps.split('/'))-1]
#        print('current map {0!s}'.format(map_name))
#        mtz_name = map_name.replace('.ccp4', '.mtz')
#        if os.path.isfile(mtz_name) and not overwrite:
#            print('WARNING: {0!s} exists; skipping...'.format(mtz_name))
#            continue
#        if axisOrder:
#            tmp_map_name = map_name.replace('.ccp4', '_tmp.ccp4')
#            map_name = change_axis_order(map_name, tmp_map_name, axisOrder)
#        run_gemmi_aap2sf(map_name, mtz_name, dmin)
#        if tmp_map_name:
#            remove_temp_map(tmp_map_name)


def usage():
    usage = (
        '\n'
        'convert_event_map_to_mtz.py converts pandda event, z and average maps to mtz format\n'
        '\n'
        'usage:\n'
        'ccp4-python convert_event_map_to_mtz.py -p <pandda_dir>\n'
        'e.g.\n'
        'ccp4-python convert_event_map_to_mtz.py -p /data/user/pandda\n'
        'Default: export all structures that have a ligand modelled as ensemble model'
        '\n'
        'additional command line options:\n'
        '--highconfidence, -a AXIS_ORDER\n'
        '    changes axis order of input map as specified, e.g. -a zyx\n'
        '--overwrite, -o\n'
        '    flag to overwrite existing mtz files\n'
    )
    print(usage)

def main(argv):
    panddaDir = None
    export = False
    highconfidenceOnly = False
    lowconfidenceOnly = False
    ensembleOnly = True
    singleOnly = False
    mixed = False

    try:
        opts, args = getopt.getopt(argv,"p:ha",["panddadir=", "export"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-p", "--panddadir"):
            panddaDir = arg
        elif opt in ("-e", "--export"):
            export = True
        elif opt in ("-hi", "--highconfidence"):
            highconfidenceOnly = True
        elif opt in ("-lo", "--lowconfidence"):
            lowconfidenceOnly = True


    if os.path.isdir(panddaDir):
        export_pandda_models(panddaDir)
    else:
        print('ERROR: pandda directory does not exist -> {0!s}'.format(panddaDir))

if __name__ == '__main__':
    main(sys.argv[1:])
