import sys
import os
import getopt
import glob
import gemmi


def help():
    msg = (
        'usage:\n'
        'ccp4-python combine_sf.py -p <process mtz/cif> -r <optional: refine mtz/cif> -e <event mtz/cif comma separated> -o <output cif>\n'
        'e.g.\n'
        'ccp4-python combine_sf.py -p process.mtz -e event_1.mtz -o combined.cif\n'
        'ccp4-python combine_sf.py -p process.mtz -r refine.mtz -e event_1.mtz,event_2.mtz -o combined.cif\n'
    )
    return msg


def convert_mtz_to_cif(sf_file, block_name):
    if sf_file.endswith('.mtz'):
        print('converting {0!s} to CIF'.format(sf_file))
        os.system('gemmi mtz2cif -b {0!s} {1!s} {2!s}'.format(block_name, sf_file, sf_file.replace('.mtz', '.cif')))
        sf_file = sf_file.replace('.mtz', '.cif')
    else:
        print('{0!s} is already in CIF format')
    return sf_file

def combine_sf_files(process, refine, event, cif_out):
    doc = gemmi.cif.Document()
    process = convert_mtz_to_cif(process, "process")
    proc = gemmi.cif.read_file(process)
    proc_block = proc.sole_block()
    proc_block.set_pair('_diffrn.details', gemmi.cif.quote('data processing'))
    proc_block.move_item(proc_block.get_index('_diffrn.details'), 2)
    doc.add_copied_block(proc_block)
    if refine:
        refine = convert_mtz_to_cif(refine, "refine")
        refi = gemmi.cif.read_file(refine)
        refi_block = refi.sole_block()
        refi_block.set_pair('_diffrn.details', gemmi.cif.quote('refinement maps'))
        refi_block.move_item(refi_block.get_index('_diffrn.details'), 2)
        doc.add_copied_block(refi_block)
    for n, e in enumerate(event.split(',')):
        event = convert_mtz_to_cif(e, "event_{0!s}".format(n))
        ev = gemmi.cif.read_file(event)
        ev_block = ev.sole_block()
        ev_block.set_pair('_diffrn.details', gemmi.cif.quote('event map {0!s}'.format(n)))
        ev_block.move_item(ev_block.get_index('_diffrn.details'), 2)
        doc.add_copied_block(ev_block)
    print('saving combined CIF file as {0!s}'.format(cif_out))
    doc.write_file(cif_out)

def main(argv):
    process = None
    refine = None
    event = None
    cif_out = None

    try:
        opts, args = getopt.getopt(argv,"p:r:e:o:h",["process=", "refine=", "event=", "output=", "help"])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            compoundlib.usage()
            sys.exit(2)
        elif opt in ("-p", "--process"):
            process = arg
        elif opt in ("-r", "--refine"):
            refine = arg
        elif opt in ("-e", "--event"):
            event = arg
        elif opt in ("-o", "--output"):
            cif_out = arg

    if os.path.isfile(process) and cif_out:
        combine_sf_files(process, refine, event, cif_out)

if __name__ == '__main__':
    main(sys.argv[1:])
