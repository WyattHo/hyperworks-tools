import json
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

    h3d_path = Path(cwd).joinpath(h3d_name)
    tcl_path = Path(__file__).parent.joinpath(tcl_name)
    
    cmd = f'hw -tcl {tcl_path} {h3d_path}'
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def main():
    config = read_configuration('config.json')
    # run_solver(config)
    retrieve_acceleration(config)


if __name__ == '__main__':
    main()
