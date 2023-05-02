import os
import sys
import gemmi
import pandas as pd

def get_ligands_in_structure(pdb, allowed_ligand_ids):
    lig_dict = {}
    structure = gemmi.read_structure(pdb)
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.name in allowed_ligand_ids:
                    c = gemmi.Chain(chain.name)
                    c.add_residue(residue, 0)
                    lig_name = str(residue.name)+'-'+str(chain.name)+'-'+ str(residue.seqid.num)
                    lig_dict[lig_name] = c
    return lig_dict


def parse_pandda_analyse_events_csv(pandda_csv, pandda_dir, allowed_ligand_ids):
    event_df = pd.read_csv(pandda_csv)
    event_df['ligand_id'] = ""
    event_df['ligand_event_distance'] = ""
    for index, row in event_df.iterrows():
        sample_id = row['dtag']
        print(sample_id)
#        event_idx = row['event_idx']
#        site_idx = row['site_idx']
        x_event = float(row['x'])
        y_event = float(row['y'])
        z_event = float(row['z'])
        position_event = gemmi.Position(x_event, y_event, z_event)
        lig_dist_list = []
        pdb = os.path.join(pandda_dir, 'processed_datasets', sample_id, 'modelled_structures',
                           sample_id + '-pandda-model.pdb')
        if os.path.isfile(pdb):
#            print(pdb)
            lig_dict = get_ligands_in_structure(pdb, allowed_ligand_ids)
            if lig_dict:
                for ligand in lig_dict:
                    print(ligand)
                    c = ligDict[ligand][0]
                    position_ligand = c.calculate_center_of_mass()
                    event_ligand_distance = position_event.dist(position_ligand)
                    lig_dist_list.append([ligand, event_ligand_distance])
                if lig_dist_list:
                    ligand_id_close_to_event = min(lig_dist_list, key=lambda x: x[1])[0]
                    ligand_event_distance = min(lig_dist_list, key=lambda x: x[1])[1]
                    event_df.at[index, 'ligand_id'] =ligand_id_close_to_event
                    event_df.at[index, 'ligand_event_distance'] =ligand_event_distance
    event_df.to_csv('pandda_analyse_events_with_ligand_ids.csv')


if __name__ == '__main__':
    allowed_ligand_ids = ['LIG, DRG', '188']
    pandda_dir = sys.argv[1]
    pandda_csv = os.path.join(pandda_dir, 'analyses', 'pandda_analyse_events.csv')
    parse_pandda_analyse_events_csv(pandda_csv, pandda_dir, allowed_ligand_ids)