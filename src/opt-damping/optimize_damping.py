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
    fem = config['fem']
    nt = config['nt']
    core = config['core']
    cmd = f'{solver} {fem} -nt {nt} -core {core}'
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def main():
    config = read_configuration('config.json')
    run_solver(config)


if __name__ == '__main__':
    main()
