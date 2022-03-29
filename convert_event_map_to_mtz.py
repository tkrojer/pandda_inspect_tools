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
import gemmi

def get_axis_order(sample_id, map_name, maps):
    print('>> checking axis order...')
    cmd = (
        'mapmask mapin {0!s} << eof > mapmask.log\n'.format(maps) +
        ' end\n'
        'eof\n'
    )

    print('running mapdump to get axis order for {0!s}'.format(map_name))
    os.system(cmd)

    if os.path.isfile('mapmask.log'):
        for line in open('mapmask.log'):
            if 'Fast, medium, slow axes' in line:
                a = line.split()[5]
                b = line.split()[6]
                c = line.split()[7]
                print('axis order of maps is : {0!s} {1!s} {2!s}'.format(a, b, c))
                break

    os.remove('mapmask.log')


def change_axis_order(map_name, tmp_map_name, axisOrder):
    if len(axisOrder) != 3:
        print('ERROR: axis order needs to contain three characters of type X, Y and Z')
        sys.exit(2)

    a = axisOrder[0].upper()
    b = axisOrder[1].upper()
    c = axisOrder[2].upper()

    cmd = (
        'mapmask mapin {0!s} mapout {1!s} << eof > /dev/null\n'.format(map_name, tmp_map_name) +
        ' axis {0!s} {1!s} {2!s}\n'.format(a, b, c) +
        ' end\n'
        'eof'
    )

    print('running mapmask to change axis order for {0!s} to {1!s}'.format(map_name, axisOrder))
    os.system(cmd)

    return tmp_map_name


def get_resolution(pandda_input_mtz):
    m = gemmi.read_mtz_file(pandda_input_mtz)
    highres = m.resolution_high()
    return highres

def run_gemmi_aap2sf(map_name, mtz_name,  dmin):
    print('>> runnning gemmi map2sf...')
    if 'z_map' in map_name:
        cmd = 'gemmi map2sf %s %s DELFWT PHDELWT --dmin=%s' % (map_name, mtz_name, dmin)
    else:
        cmd = 'gemmi map2sf %s %s FWT PHWT --dmin=%s' % (map_name, mtz_name, dmin)
    os.system(cmd)

def remove_temp_map(tmp_map_name):
    if os.path.isfile(tmp_map_name):
        os.remove(tmp_map_name)

def convert_event_maps_to_mtz(panddaDir, axisOrder, overwrite, checkOrder):
    print('>>> looking for event maps in {0!s}'.format(panddaDir))
    sampleList = []
    for maps in sorted(glob.glob(os.path.join(panddaDir, 'processed_datasets', '*', '*.ccp4'))):
        tmp_map_name = None
        sample_id = maps.split('/')[len(maps.split('/'))-2]
        map_name = maps.split('/')[len(maps.split('/'))-1]
        if checkOrder:
            get_axis_order(sample_id, map_name, maps)
            break
        if sample_id not in sampleList:
            print('converting maps for {0!s}'.format(sample_id))
            sampleList.append(sample_id)
        workDir = maps[:maps.rfind('/')]
        os.chdir(workDir)
        pandda_input_mtz = '{0!s}-pandda-input.mtz'.format(sample_id)
        if os.path.isfile(pandda_input_mtz):
            dmin = get_resolution(pandda_input_mtz)
        else:
            print('ERROR: {0!s} does not exist; cannot get resolution of map later; skipping...'.format(pandda_input_mtz))
            sys.exit(2)
        print('current map {0!s}'.format(map_name))
        mtz_name = map_name.replace('.ccp4', '.mtz')
        if os.path.isfile(mtz_name) and not overwrite:
            print('WARNING: {0!s} exists; skipping...'.format(mtz_name))
            continue
        if axisOrder:
            tmp_map_name = map_name.replace('.ccp4', '_tmp.ccp4')
            map_name = change_axis_order(map_name, tmp_map_name, axisOrder)
        run_gemmi_aap2sf(map_name, mtz_name, dmin)
        if tmp_map_name:
            remove_temp_map(tmp_map_name)


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
    axisOrder = None
    checkOrder = False
    overwrite = False

    try:
        opts, args = getopt.getopt(argv,"p:a:hoc",["panddadir=", "axis=", "overwrite", "checkaxis"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-p", "--panddadir"):
            panddaDir = arg
        elif opt in ("-a", "--axis"):
            axisOrder = arg
        elif opt in ("-c", "--checkaxis"):
            checkOrder = True
        elif opt in ("-o", "--overwrite"):
            overwrite = True

    if os.path.isdir(panddaDir):
        convert_event_maps_to_mtz(panddaDir, axisOrder, overwrite, checkOrder)
    else:
        print('ERROR: pandda directory does not exist -> {0!s}'.format(panddaDir))

if __name__ == '__main__':
    main(sys.argv[1:])
