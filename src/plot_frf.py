import configparser
import csv
import os
from typing import Dict, List

import matplotlib.pyplot as plt


this_dir = os.path.dirname(__file__)
config_file = os.path.join(this_dir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)

DATA_DIR = config['FRF']['DATA_DIR']
CURVE_NUM_EACH_PLOT = eval(config['FRF']['CURVE_NUM_EACH_PLOT'])
TIME_RANGE = eval(config['FRF']['TIME_RANGE'])


class Curve:
    def __init__(self) -> None:
        self.time = []
        self.phase = []
        self.mag = []


    def get_mag_max(self) -> float:
        return max(self.mag)


Curves = Dict[str, Curve]


class Analysis:
    def __init__(self, curves: Curves) -> None:
        self.curves = curves

    
    def fetch_main_curves(self) -> List[str]:
        curve_names = list(self.curves.keys())
        max_values = []
        for curve_name in curve_names:
            max_values.append(self.curves[curve_name].get_mag_max())
        max_values_ascending = max_values.copy()
        max_values_ascending.sort(reverse=True)
        rank_indices = [max_values.index(val) for val in max_values_ascending[:CURVE_NUM_EACH_PLOT]]
        main_curve_names = [curve_names[idx] for idx in rank_indices]
        return main_curve_names


Analyses = Dict[str, Analysis]


def initial_curves(fieldnames: str) -> Curves:
    curves = {}
    for field_name in fieldnames:
        if field_name != 'Time':
            curve_name = field_name.split('-')[0]
            if curve_name not in curves:
                curves[curve_name] = Curve()
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
                    curve.mag.append(1000 * float(row[field_name_mag]))
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


def plot_curves(analyses: Analyses, analysis_name: str, main_curve_names: List[str]):
    fig = plt.figure(figsize=(6, 2.4), tight_layout=True)
    ax = plt.axes()
    for curve_name in main_curve_names:
        curve = analyses[analysis_name].curves[curve_name]
        time = curve.time
        mag = curve.mag
        ax.plot(time, mag, label=curve_name, linewidth=1.0)
    ax.set_title(analysis_name)
    ax.set_ylabel('deformation, mm')
    ax.set_xlabel('frequency, Hz')
    ax.grid(visible=True, axis='both')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.show() 


def main():
    analyses = get_analyses()
    for analysis_name, analysis in analyses.items():
        main_curve_names = analysis.fetch_main_curves()
        plot_curves(analyses, analysis_name, main_curve_names)

if __name__ == '__main__':
    main()
