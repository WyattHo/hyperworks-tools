import json
import pandas as pd
import subprocess
from pathlib import Path


def read_configuration(config_name: str) -> dict:
    this_dir = Path(__file__).parent
    config_path = this_dir.joinpath(config_name)
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def run_solver(config: dict) -> subprocess.CompletedProcess:
    cwd = config['cwd']
    solver = config['solver']
    fem = config['model'] + '.fem'
    nt = config['nt']
    core = config['core']
    cmd = f'{solver} {fem} -nt {nt} -core {core}'
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def retrieve_acceleration(config: dict):
    cwd = config['cwd']
    h3d_name = config['model'] + '.h3d'
    tcl_name = config['tcl_name']
    nodes = ','.join([f'{idx}' for idx in config['nodes']])

    h3d_path = Path(cwd).joinpath(h3d_name)
    tcl_path = Path(__file__).parent.joinpath(tcl_name)

    cmd = f'hw -tcl {tcl_path} {h3d_path} {nodes}'
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def get_peak_response(config: dict) -> list[float]:
    cwd = config['cwd']
    csv_name = config['model'] + '-subcase2.csv'
    target = config['target']
    G = 9806.65

    csv_path = Path(cwd).joinpath(csv_name)
    df = pd.read_csv(csv_path)
    peak_freq, peak_acc = 0, 0
    for col in df.columns:
        if not col.startswith('Time'):
            max_acc = df[col].max()
            max_idx = df[col].idxmax()
            if max_acc > peak_acc:
                peak_acc = max_acc
                peak_freq = df['Time'].iloc[max_idx]
    return [peak_freq, peak_acc / G]


def main():
    config = read_configuration('config.json')
    # run_solver(config)
    # retrieve_acceleration(config)
    peak_freq, peak_acc = get_peak_response(config)


if __name__ == '__main__':
    main()
