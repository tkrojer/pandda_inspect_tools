import getopt
import glob
import sys
import os
import gemmi


def change_axis_order():
    print('hallo')

def convert_event_maps_to_mtz(panddaDir, axisOrder):
    print('looking for event maps in {0!s}'.format(panddaDir))
    for maps in sorted(glob.glob(os.path.join(panddaDir, 'processed_datasets', '*', '*.ccp4'))):
        sample_id = maps.split('/')[len(maps.split('/'))-2]
        os.chdir(maps[:maps.rfind('/')])
        map_name = maps.split('/')[len(maps.split('/'))-1]
        print(map_name)
        if axisOrder:
            change_axis_order()

def main(argv):
    panddaDir = None
    axisOrder = None

    try:
        opts, args = getopt.getopt(argv,"hp:a:",["panddadir=", "axis="])
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

    if os.path.isdir(panddaDir):
        convert_event_maps_to_mtz(panddaDir, axisOrder)

if __name__ == '__main__':
    main(sys.argv[1:])
