import json
import pandas as pd
from pathlib import Path


# Configurations
this_dir = Path(__file__).parent
config_path = this_dir.joinpath('config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

data_dir = Path(config['rel_disp']['data_dir'])
directions = config['rel_disp']['directions']
node_pairs = config['rel_disp']['node_pairs']
csv_paths = list(data_dir.glob('*.csv'))


# Create output directory
output_dir = data_dir.joinpath('output')
output_dir.mkdir(parents=True, exist_ok=True)


# Calculate relative displacements for each mountings
csv_results = {}
for path in csv_paths:
    df = pd.read_csv(str(path))
    mount_results = {}
    for position, [node1, node2] in node_pairs.items():
        nodepair_results = {}
        for direction in directions:
            column1 = f'N{node1} - {direction}-Mag'
            column2 = f'N{node2} - {direction}-Mag'
            abs_disp_node1_values = df[column1]
            abs_disp_node2_values = df[column2]
            rel_disp_values = abs_disp_node2_values - abs_disp_node1_values
            nodepair_results[direction] = rel_disp_values.abs()
            if 'frequency' not in nodepair_results:
                nodepair_results['frequency'] = df['Time']
        mount_results[position] = pd.DataFrame(nodepair_results)
    csv_results[path.stem] = mount_results


# Calculate maximum relative displacements considering all mountings
for input_filename, mount_results in csv_results.items():
    max_rel_disp_results = {}
    for direction in directions:
        all_rel_disp_results = {}
        for position, nodepair_results in mount_results.items():
            all_rel_disp_results[position] = nodepair_results[direction]
            if 'frequency' not in max_rel_disp_results:
                max_rel_disp_results['frequency'] = nodepair_results['frequency']
        max_rel_disp_results[direction] = pd.DataFrame(all_rel_disp_results).max(axis=1)
        
    output_filename = f'relative-{input_filename}.csv'
    output_path = output_dir.joinpath(output_filename)
    df = pd.DataFrame(max_rel_disp_results)
    df.to_csv(output_path, index=False)
