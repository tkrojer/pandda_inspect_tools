import gemmi
import os

bound_occ = 0.3

ground = gemmi.read_structure('init.pdb')
bound = gemmi.read_structure('pandda.pdb')

ground_model = ground[0]
bound_model = bound[0]

print('setting occupancy of ground state to {0!s}'.format(1.0-bound_occ))
for cra in ground_model.all():
	current_occ = cra.atom.occ
	cra.atom.occ = current_occ - current_occ * 0.3

print('setting occupancy of bound state to {0!s}\n'.format(bound_occ))
for cra in bound_model.all():
	current_occ = cra.atom.occ
	cra.atom.occ = current_occ * 0.3

# the bound state should be the first since it is the scientifically most relevant
print('combining bound & ground state as separate models in ensemble.pdb\n')
bound.add_model(ground_model, pos=2)
bound.write_pdb('ensemble.pdb')

print('running pdb_extract to convert PDB in CIF file using -NMR option to preserve models')
os.system('pdb_extract -iPDB ensemble.pdb -o ensemble.mmcif -NMR > pdb_extract.log')
print('finished running pdb_extract\n')

print('doing zero cycles of refmac5 to determine refinement statistics of ensemble model')
print('note: hklout cannot directly be used for PDB upload since MODEL entries get messed up')
print('running refmac5...')
cmd = ( 'refmac5 hklin free.mtz hklout ensemble.mtz xyzin ensemble.pdb xyzout refmac.pdb libin VT00025.cif << eof > refmac.log\n'
	'ncyc 0\n'
	'end\n'
	'eof\n'
	)
os.system(cmd)
print('finished running refmac5\n')

# remove loop/ table
print('reading refinement statistics from refmac.mmcif with gemmi')
s = gemmi.cif.read_file('refmac.mmcif')
#b = s.sole_block()
for b in s:
	if b.name == "XXXX":
		coordinate_block = b
		header = b.find_loop('_atom_site.group_PDB').get_loop().tags
		table = b.find(header)
		print('removing _atom_site table from refmac.mmcif')
		table.erase()
		break

print('reading ensemble.mmcif from pdb_extract with gemmi')
e = gemmi.cif.read_file('ensemble.mmcif')
eb = e.sole_block()
print('moving _atom_site table from ensemble.mmcif into list')
atom_site_header = eb.find_loop('_atom_site.group_PDB').get_loop().tags
# need to do this, otherwise end up with _atom_site._atom_site.group_PDB in xyz_table below
atom_site_labels = []
for i in atom_site_header:
	atom_site_labels.append(i.replace('_atom_site.', ''))

xyz = eb.find(atom_site_header)
print('creating _atom_site table in refmac.mmcif')
xyz_table = coordinate_block.init_loop('_atom_site.', atom_site_labels)
print('adding rows from ensemble.mmcif _atom_site table to _atom_site table in refmac.mmcif')
for row in xyz:
	if not row['_atom_site.type_symbol'] == 'H':
		xyz_table.add_row(row)
print('finished adding rows')

print('saving final mmcif file')
s.write_file('test.mmcif')


