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
    for n, item in enumerate(inspect_csv):  # number of columns at the end can differ
        if item == 'Ligand Confidence':
            ligand_confidence_index = n
            break
    return ligand_confidence_index

def get_info(inspect_csv, sample_id, ligand_confidence_index):
    table = []
    header = ['Event', 'Site', 'BDC', 'Ligand confidence']
    for item in inspect_csv:
        if item[0] == sample_id:
            table.append([item[1], item[11], item[2], item[ligand_confidence_index]])
    print(tabulate(table), headers=header)

def export_pandda_models(panddaDir, analyseOnly):
    inspect_csv = read_inspect_event_csv_as_list(panddaDir)
    ligand_confidence_index = get_ligand_confidence_index(inspect_csv)
    for maps in sorted(glob.glob(os.path.join(panddaDir, 'processed_datasets', '*',
                                              'modelled_structures','*-pandda-model.pdb'))):
        sample_id = maps.split('/')[len(maps.split('/'))-3]
        print('{0!s}:'.format(sample_id))
        get_info(inspect_csv, sample_id, ligand_confidence_index)



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
        '\n'
        'additional command line options:\n'
        '--axis, -a AXIS_ORDER\n'
        '    changes axis order of input map as specified, e.g. -a zyx\n'
        '--overwrite, -o\n'
        '    flag to overwrite existing mtz files\n'
    )
    print(usage)

def main(argv):
    panddaDir = None
    analyseOnly = False

    try:
        opts, args = getopt.getopt(argv,"p:ha",["panddadir=", "analyse"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-p", "--panddadir"):
            panddaDir = arg
        elif opt in ("-a", "--analyse"):
            analyseOnly = True

    if os.path.isdir(panddaDir):
        export_pandda_models(panddaDir, analyseOnly)
    else:
        print('ERROR: pandda directory does not exist -> {0!s}'.format(panddaDir))

if __name__ == '__main__':
    main(sys.argv[1:])
