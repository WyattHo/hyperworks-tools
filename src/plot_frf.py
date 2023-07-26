import csv
import json
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits import mplot3d


this_dir = os.path.dirname(__file__)
config_path = os.path.join(this_dir, 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

DATA_DIR = config['frf']['data_dir']
CURVE_NUM_EACH_PLOT = config['frf']['curve_num_each_plot']
TIME_RANGE = config['frf']['time_range']
FEM_PATH = config['frf']['fem_path']


Coordinate = Tuple[float, float, float]


class Curve:
    def __init__(self, node_idx: int) -> None:
        self.node_idx = node_idx
        self.time = []
        self.phase = []
        self.mag = []

    def get_mag_max(self) -> float:
        return max(self.mag)

    def assign_coordinate(self, coordinate: Coordinate):
        self.coordinate = coordinate


Curves = Dict[str, Curve]


class Analysis:
    def __init__(self, curves: Curves) -> None:
        self.curves = curves

    def fetch_main_curve_names(self) -> List[str]:
        curve_names = list(self.curves.keys())
        max_values = []
        for curve_name in curve_names:
            max_values.append(self.curves[curve_name].get_mag_max())
        max_values_ascending = max_values.copy()
        max_values_ascending.sort(reverse=True)
        rank_indices = [
            max_values.index(val) 
            for val in max_values_ascending[:CURVE_NUM_EACH_PLOT]
        ]
        main_curve_names = [curve_names[idx] for idx in rank_indices]
        return main_curve_names


Analyses = Dict[str, Analysis]


def initial_curves(fieldnames: str) -> Curves:
    curves = {}
    for field_name in fieldnames:
        if field_name != 'Time':
            curve_name = field_name.split('-')[0]
            if curve_name not in curves:
                node_idx = eval(curve_name.strip('N'))
                curves[curve_name] = Curve(node_idx)
    return curves


def get_curves(file_path: str) -> Curves:
    with open(file_path, 'r') as f:
        table = csv.DictReader(f, delimiter=',', skipinitialspace=True)
        curves = initial_curves(table.fieldnames)
        for row in table:
            for curve_name, curve in curves.items():
                field_name_time = 'Time'
                field_name_phase = '-'.join([curve_name, 'Phase'])
                field_name_mag = '-'.join([curve_name, 'Mag'])
                time = float(row[field_name_time])
                if min(TIME_RANGE) <= time <= max(TIME_RANGE):
                    curve.time.append(time)
                    curve.phase.append(float(row[field_name_phase]))
                    curve.mag.append(1.0E+06 * float(row[field_name_mag]))
    return curves


def get_analyses() -> Analyses:
    analyses = {}
    file_names = os.listdir(DATA_DIR)
    for file_name in file_names:
        if not file_name.endswith('.csv'):
            continue
        analysis_name = file_name.strip('.csv')
        file_path = os.path.join(DATA_DIR, file_name)
        analyses[analysis_name] = Analysis(get_curves(file_path))
    return analyses


def validate_coordinate(coord: str) -> float:
    sci_notation = False
    if coord.startswith('-'):
        if '-' in coord[1:]:
            sci_notation = True
    else:
        if '-' in coord:
            sci_notation = True
    if sci_notation:
        idx = coord.rindex('-')
        coefficient = coord[:idx]
        power = coord[idx:]
        return eval(f'{coefficient}E{power}')
    else:
        return eval(coord)


def parse_coordinate(line: str) -> Coordinate:
    coord_x = validate_coordinate(line[24:32]) * 1000
    coord_y = validate_coordinate(line[32:40]) * 1000
    coord_z = validate_coordinate(line[40:48]) * 1000
    return (coord_x, coord_y, coord_z)


def check_node(analyses: Analyses, node_key: str):
    for analysis in analyses.values():
        if node_key in analysis.curves.keys():
            return True
    return False


def assign_coordinate(analyses: Analyses, node_key: str, coordinate: Coordinate):
    for analysis in analyses.values():
        analysis.curves[node_key].assign_coordinate(coordinate)


def parse_fem_and_assign_coordinates(analyses: Analyses, fem_path: str = FEM_PATH):
    with open(fem_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('GRID'):
            node_idx = eval(line[8:16])
            node_key = f'N{node_idx:d}'
            if check_node(analyses, node_key):
                coordinate = parse_coordinate(line)
                assign_coordinate(
                    analyses,
                    node_key,
                    coordinate
                )


def plot_main_curves(analyses: Analyses, analysis_name: str, main_curve_names: List[str]):
    fig = plt.figure(figsize=(6, 2.4), tight_layout=True)
    ax = plt.axes()
    for curve_name in main_curve_names:
        curve = analyses[analysis_name].curves[curve_name]
        time = curve.time
        mag = curve.mag
        ax.plot(time, mag, label=curve_name, linewidth=1.0)
    ax.set_title(analysis_name)
    ax.set_ylabel('deformation, $\mu m$')
    ax.set_xlabel('frequency, Hz')
    ax.grid(visible=True, axis='both')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.show()


def plot_3d_distribution(analyses: Analyses, analysis_name: str, case: str):
    fig = plt.figure(figsize=(9, 6), tight_layout=True)
    ax = plt.axes(projection='3d')

    if case == 'top':
        elev = 90
        zrange = [50.0, 150.0]
    else:
        elev = -90
        zrange = [-50.0, 50.0]

    x, y, z = [], [], []
    for curve_name, curve in analyses[analysis_name].curves.items():
        coord_x, coord_y, coord_z = curve.coordinate
        if min(zrange) < coord_z < max(zrange):
            deformation_max = max(curve.mag)
            x.append(coord_x)
            y.append(coord_y)
            z.append(deformation_max)

    scatter = ax.scatter(x, y, z, c=z, cmap=plt.get_cmap('jet'))
    ax.view_init(elev=elev, azim=0, roll=0)
    ax.set_proj_type('ortho')
    ax.set_title(f'{analysis_name} - {case}')
    ax.set_xlabel('x, mm')
    ax.set_ylabel('y, mm')
    ax.set_zticks([])
    ax.set_aspect('equalxy')
    fig.colorbar(
        scatter, shrink=0.3, aspect=20,
        location='left', label='deformation, $\mu m$',
    )
    plt.show()


def main():
    analyses = get_analyses()
    parse_fem_and_assign_coordinates(analyses)
    for analysis_name, analysis in analyses.items():
        main_curve_names = analysis.fetch_main_curve_names()
        plot_main_curves(analyses, analysis_name, main_curve_names)
        for case in ['top', 'bottom']:
            plot_3d_distribution(analyses, analysis_name, case)


if __name__ == '__main__':
    main()
