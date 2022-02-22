import getopt
import glob
import sys
import os
import gemmi


def convert_event_maps_to_mtz(panddaDir):
    print('looking for event maps in {0!s}'.format(panddaDir))
    for maps in sorted(glob.glob(os.path.join(panddaDir, 'processed_datasets', '*', '*.ccp4'))):
        sample_id = maps.split('/')[len(maps.split('/'))-2]
        print(sample_id, maps[:maps.rfind('/')])
        os.chdir(maps[:maps.rfind('/')])
        print(os.getcwd())
        


def main(argv):
    panddaDir = None

    try:
        opts, args = getopt.getopt(argv,"hp:",["pdir="])
    except getopt.GetoptError:
        print('ccp4-python convert_event_map_to_mtz.py -p <pandda_dir>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('ccp4-python convert_event_map_to_mtz.py -p <pandda_dir>')
            sys.exit()
        elif opt in ("-p", "--pdir"):
            panddaDir = arg

    if os.path.isdir(panddaDir):
        convert_event_maps_to_mtz(panddaDir)

if __name__ == '__main__':
    main(sys.argv[1:])
