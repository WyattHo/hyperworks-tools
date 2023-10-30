import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


def read_configuration(config_name: str) -> dict:
    this_dir = Path(__file__).parent
    config_path = this_dir.joinpath(config_name)
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


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

    def fetch_main_curve_names(self, curve_num: int) -> List[str]:
        curve_names = list(self.curves.keys())
        max_values = []
        for curve_name in curve_names:
            max_values.append(self.curves[curve_name].get_mag_max())
        max_values_ascending = max_values.copy()
        max_values_ascending.sort(reverse=True)
        rank_indices = [
            max_values.index(val)
            for val in max_values_ascending[:curve_num]
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


def get_curves(file_path: str, time_range: List) -> Curves:
    with open(file_path, 'r') as f:
        table = csv.DictReader(f, delimiter=',', skipinitialspace=True)
        curves = initial_curves(table.fieldnames)
        for row in table:
            for curve_name, curve in curves.items():
                field_name_time = 'Time'
                field_name_phase = '-'.join([curve_name, 'Phase'])
                field_name_mag = '-'.join([curve_name, 'Mag'])
                time = float(row[field_name_time])
                if min(time_range) <= time <= max(time_range):
                    curve.time.append(time)
                    curve.phase.append(float(row[field_name_phase]))
                    curve.mag.append(1.0E+06 * float(row[field_name_mag]))
    return curves


def get_analyses(data_dir: Path, time_range: List) -> Analyses:
    analyses = {}
    file_names = data_dir.iterdir()
    for file_name in file_names:
        if file_name.suffix != '.csv':
            continue
        analysis_name = file_name.stem
        curves = get_curves(file_name, time_range)
        analyses[analysis_name] = Analysis(curves)
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


def parse_fem_and_assign_coordinates(analyses: Analyses, fem_path: str):
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


def plot_main_curves(
        analyses: Analyses, analysis_name: str,
        main_curve_names: List[str], output_dir: Path):
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
    fig_name = output_dir.joinpath(f'{analysis_name}.png')
    fig.savefig(fig_name)


def plot_distribution(
        analyses: Analyses, analysis_name: str, case: str,
        top_view: str, bottom_view: str, output_dir: Path):
    fig = plt.figure(figsize=(6, 4), tight_layout=True)
    ax = plt.axes()

    if case == 'top':
        zrange = [50.0, 150.0]
    else:
        zrange = [-50.0, 50.0]

    x, y, z = [], [], []
    for curve in analyses[analysis_name].curves.values():
        coord_x, coord_y, coord_z = curve.coordinate
        if min(zrange) < coord_z < max(zrange):
            deformation_max = max(curve.mag)
            x.append(coord_y)
            y.append(coord_x)
            z.append(deformation_max)

    scatter = ax.scatter(x, y, c=z, cmap=plt.get_cmap('OrRd'))
    ax.set_xlabel('y, mm')
    ax.set_ylabel('x, mm')
    ax.set_aspect('equal')
    if case == 'top':
        ax.invert_yaxis()
        img = plt.imread(top_view)
        ax.imshow(img, extent=[-2, 359, 171, -79])
    else:
        img = plt.imread(bottom_view)
        ax.imshow(img, extent=[-2, 359, -79, 171])

    fig.colorbar(
        scatter, shrink=0.6, aspect=20,
        location='left', label='deformation, $\mu m$',
        pad=0.15
    )
    fig_name = output_dir.joinpath(f'{analysis_name}_{case}.png')
    fig.savefig(fig_name)


def main(config_name: str):
    # Parse config
    config = read_configuration(config_name)
    output_dir = Path(config['output'])
    data_dir = Path(config['frf']['data_dir'])
    curve_num = config['frf']['curve_num_each_plot']
    time_range = config['frf']['time_range']
    fem_path = config['frf']['fem_path']
    top_view = config['frf']['top_view']
    bottom_view = config['frf']['bottom_view']

    # Process data
    analyses = get_analyses(data_dir, time_range)
    parse_fem_and_assign_coordinates(analyses, fem_path)

    # Plot
    output_dir.mkdir(parents=True, exist_ok=True)
    for analysis_name, analysis in analyses.items():
        main_curve_names = analysis.fetch_main_curve_names(curve_num)
        plot_main_curves(analyses, analysis_name, main_curve_names, output_dir)
        for case in ['top', 'bottom']:
            plot_distribution(
                analyses, analysis_name, case,
                top_view, bottom_view, output_dir
            )


if __name__ == '__main__':
    main('config_test.json')
