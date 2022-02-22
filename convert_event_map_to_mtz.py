import getopt
import glob
import sys
import os
import gemmi


def change_axis_order(map_name, axisOrder):
    if len(axisOrder) != 3:
        print('ERROR: axis order needs to contain three characters of type X, Y and Z')
        sys.exit(2)

    a = axisOrder[0].upper()
    b = axisOrder[1].upper()
    c = axisOrder[2].upper()

    cmd = (
        'mapmask mapin {0!s} mapout {1!s} << eof\n'.format(map_name, map_name.replace('.ccp4', '_tmp.ccp4')) +
        ' axis {0!s} {1!s} {2!s}\n'.format(a, b, c) +
        ' end\n'
        'eof'
    )

    print(cmd)

def convert_event_maps_to_mtz(panddaDir, axisOrder, overwrite):
    if overwrite:
        print('ALARM')
        sys.exit(2)

    print('looking for event maps in {0!s}'.format(panddaDir))
    for maps in sorted(glob.glob(os.path.join(panddaDir, 'processed_datasets', '*', '*.ccp4'))):
        sample_id = maps.split('/')[len(maps.split('/'))-2]
        os.chdir(maps[:maps.rfind('/')])
        map_name = maps.split('/')[len(maps.split('/'))-1]
        print(map_name)
        if axisOrder:
            change_axis_order(map_name, axisOrder)

def main(argv):
    panddaDir = None
    axisOrder = None
    overwrite = False

    try:
        opts, args = getopt.getopt(argv,"hp:a:o:",["panddadir=", "axis=", "overwrite"])
    except getopt.GetoptError:
        print('ccp4-python convert_event_map_to_mtz.py -p <pandda_dir> -a <axis>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('ccp4-python convert_event_map_to_mtz.py -p <pandda_dir>')
            sys.exit()
        elif opt in ("-p", "--panddadir"):
            panddaDir = arg
        elif opt in ("-a", "--axis"):
            overwrite = True

    if os.path.isdir(panddaDir):
        convert_event_maps_to_mtz(panddaDir, axisOrder, overwrite)

if __name__ == '__main__':
    main(sys.argv[1:])
