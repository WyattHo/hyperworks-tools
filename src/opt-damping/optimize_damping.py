import json
import logging
import logging.config
import pandas as pd
import subprocess
from pathlib import Path


def read_configuration(config_name: str) -> dict:
    this_dir = Path(__file__).parent
    config_path = this_dir.joinpath(config_name)
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def run_solver(config: dict, model: str, logger: logging.Logger) -> subprocess.CompletedProcess:
    cwd = config['cwd']
    solver = config['solver']
    fem = model + '.fem'
    nt = config['nt']
    core = config['core']
    cmd = f'{solver} {fem} -nt {nt} -core {core}'
    logger.info(f'Executing command: {cmd}')
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def retrieve_acceleration(config: dict, model: str, logger: logging.Logger) -> subprocess.CompletedProcess:
    cwd = config['cwd']
    h3d_name = model + '.h3d'
    tcl_name = config['tcl_name']
    nodes = ','.join([f'{idx}' for idx in config['nodes']])

    h3d_path = Path(cwd).joinpath(h3d_name)
    tcl_path = Path(__file__).parent.joinpath(tcl_name)

    cmd = f'hw -tcl {tcl_path} {h3d_path} {nodes}'
    logger.info(f'Executing command: {cmd}')
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def get_peak_response(config: dict, model: str, logger: logging.Logger) -> list[float]:
    cwd = config['cwd']
    csv_name = model + '-subcase2.csv'
    G = 9806.65

    csv_path = Path(cwd).joinpath(csv_name)
    df = pd.read_csv(csv_path)
    peak_freq, peak_acc = 0, 0
    for col in df.columns:
        if not col.startswith('Time'):
            max_acc = df[col].max() / G
            max_idx = df[col].idxmax()
            if max_acc > peak_acc:
                peak_acc = max_acc
                peak_freq = df['Time'].iloc[max_idx]
    logger.info(f'peak_freq: {peak_freq:.3f}Hz. peak_acc: {peak_acc:.3f}g')
    return [peak_freq, peak_acc]


def check_tolerance(config: dict, peak_acc: float):
    tgt_acc = config['target'][-1]
    tolerance = config['tolerance_percentage']
    error = (peak_acc - tgt_acc) / tgt_acc * 100
    if -tolerance < error < tolerance:
        return True
    else:
        return False


def get_fem_info(config: dict, model: str) -> dict:
    cwd = config['cwd']
    rubber_name = config['rubber_name']
    fem = model + '.fem'
    with open(Path(cwd).joinpath(fem), 'r') as f:
        lines = f.readlines()
    for row_idx, line in enumerate(lines):
        if line.startswith('$HMNAME MAT') and rubber_name in line:
            break
    row_idx += 2
    rubber_data = lines[row_idx]
    damping = float(rubber_data[64:])
    return {'lines': lines, 'damping': damping, 'row_idx': row_idx}


def create_fem_with_damping(lines: list[str], row_idx: int, damping: float, fem_path: str):
    rubber_data_temp = lines[row_idx][0:64] + f'{damping:<8.4f}\n'
    lines_temp = lines.copy()
    lines_temp[row_idx] = rubber_data_temp
    with open(fem_path, 'w') as f:
        f.writelines(lines_temp)


def calculate_next_damping(config: dict, fem_info: dict, peak_acc_ori: float, logger: logging.Logger) -> float:
    DAMPING_DELTA = 0.0002
    lines, damping_ori, row_idx = list(fem_info.values())
    damping_tmp = damping_ori + DAMPING_DELTA
    
    cwd = config['cwd']
    model_tmp = 'temp'
    fem_path_tmp = Path(cwd).joinpath(f'{model_tmp}.fem')
    create_fem_with_damping(lines, row_idx, damping_tmp, fem_path_tmp)
    run_solver(config, model_tmp, logger)
    retrieve_acceleration(config, model_tmp, logger)
    peak_freq_tmp, peak_acc_tmp = get_peak_response(config, model_tmp, logger)

    tgt_acc = config['target'][-1]
    error_acc_ori = peak_acc_ori - tgt_acc
    error_acc_tmp = peak_acc_tmp - tgt_acc
    slope = (error_acc_tmp - error_acc_ori) / DAMPING_DELTA
    damping_next = damping_ori - (error_acc_ori / slope)
    logger.info(f'damping_ori: {damping_ori}, damping_next: {damping_next}')
    return damping_next


def main():
    config = read_configuration('config.json')
    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger()
    logger.info('Start.')

    itr = 0
    model = config['model']
    while True:
        run_solver(config, model, logger)
        retrieve_acceleration(config, model, logger)
        peak_freq, peak_acc = get_peak_response(config, model, logger)

        if check_tolerance(config, peak_acc):
            logger.info('Converged!')
            break

        itr += 1
        if itr > config['iteration_limit']:
            logger.info('Reached the iteration limit.')
            break

        fem_info = get_fem_info(config, model)
        damping_next = calculate_next_damping(config, fem_info, peak_acc, logger)
        if itr == 1:
            model += f'-itr{itr:03d}'
        else:
            model = model[0:-7] + f'-itr{itr:03d}'

        fem_path = Path(config['cwd']).joinpath(f'{model}.fem')
        create_fem_with_damping(fem_info['lines'], fem_info['row_idx'], damping_next, fem_path)
    logger.info('End.')


if __name__ == '__main__':
    main()
