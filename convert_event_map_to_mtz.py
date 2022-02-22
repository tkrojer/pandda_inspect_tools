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

    map_out = map_name.replace('.ccp4', '_tmp.ccp4')

    cmd = (
        'mapmask mapin {0!s} mapout {1!s} << eof\n'.format(map_name, map_out) +
        ' axis {0!s} {1!s} {2!s}\n'.format(a, b, c) +
        ' end\n'
        'eof'
    )

    print(cmd)

    return map_out


def get_resolution(pandda_input_mtz):
    m = gemmi.read_mtz_file(pandda_input_mtz)
    highres = m.resolution_high()
    return highres

def run_gemmi_aap2sf(map_name, mtz_name,  dmin):
    cmd = 'gemmi map2sf %s %s FWT PHWT --dmin=%s' % (map_name, mtz_name, dmin)
    print(cmd)

def convert_event_maps_to_mtz(panddaDir, axisOrder, overwrite):
    if overwrite:
        print('ALARM')
        sys.exit(2)

    print('looking for event maps in {0!s}'.format(panddaDir))
    for maps in sorted(glob.glob(os.path.join(panddaDir, 'processed_datasets', '*', '*.ccp4'))):
        dmin = None
        sample_id = maps.split('/')[len(maps.split('/'))-2]
        workDir = maps[:maps.rfind('/')]
        os.chdir(workDir)
        pandda_input_mtz = '{0!s}-pandda-input.mtz'.format(sample_id)
        if os.path.isfile(pandda_input_mtz):
            dmin = get_resolution(pandda_input_mtz)
        else:
            print('ERROR: {0!s} does not exist; cannot get resolution of map later; skipping...'.format(pandda_input_mtz))
            sys.exit(2)
        map_name = maps.split('/')[len(maps.split('/'))-1]
        mtz_name = map_name.replace('.ccp4', '.mtz')
        print(map_name)
        if axisOrder:
            map_name = change_axis_order(map_name, axisOrder)
        run_gemmi_aap2sf(map_name, mtz_name, dmin)

def main(argv):
    panddaDir = None
    axisOrder = None
    overwrite = False

    try:
        opts, args = getopt.getopt(argv,"p:a:ho",["panddadir=", "axis=", "overwrite"])
        print(opts, args)
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
            axisOrder = arg
        elif opt in ("-o", "--overwrite"):
            overwrite = True

    if os.path.isdir(panddaDir):
        convert_event_maps_to_mtz(panddaDir, axisOrder, overwrite)
    else:
        print('ERROR: pandda directory does not exist -> {0!s}'.format(panddaDir))

if __name__ == '__main__':
    main(sys.argv[1:])
