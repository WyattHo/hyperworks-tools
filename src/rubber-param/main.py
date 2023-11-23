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


def tick_fem(config: dict, model_name: str) -> tuple[list[str], int]:
    cwd = config['cwd']
    rubber_name = config['tunning']['rubber_name']
    fem = model_name + '.fem'
    with open(Path(cwd).joinpath(fem), 'r') as f:
        lines = f.readlines()
    for row_idx, line in enumerate(lines):
        if line.startswith('$HMNAME MAT') and rubber_name in line:
            break
    row_idx += 2
    return lines, row_idx


def retrieve_parameters(rubber_data: str) -> tuple[float, float]:
    elastic = float(rubber_data[16:24])
    damping = float(rubber_data[64:])
    return elastic, damping


def run_model(config: dict, model_name: str, logger: logging.Logger) -> tuple[float, float]:
    # run_solver(config, model_name, logger)
    # postprocess_h3d(config, model_name, logger)
    return read_csv_data(config, model_name)


def run_solver(config: dict, model_name: str, logger: logging.Logger) -> subprocess.CompletedProcess:
    cwd = config['cwd']
    solver = config['solve']['solver']
    fem = model_name + '.fem'
    nt = config['solve']['nt']
    core = config['solve']['core']
    cmd = f'{solver} {fem} -nt {nt} -core {core}'
    logger.info(f'Solving: {fem}')
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def postprocess_h3d(config: dict, model_name: str, logger: logging.Logger) -> subprocess.CompletedProcess:
    cwd = config['cwd']
    h3d_name = model_name + '.h3d'
    tcl_name = config['export']['tcl_name']
    nodes = ','.join([f'{idx}' for idx in config['export']['nodes']])

    h3d_path = Path(cwd).joinpath(h3d_name)
    tcl_path = Path(__file__).parent.joinpath(tcl_name)

    cmd = f'hw -tcl {tcl_path} {h3d_path} {nodes}'
    logger.info(f'Executing: {tcl_path}')
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def read_csv_data(config: dict, model_name: str) -> tuple[float, float]:
    cwd = config['cwd']
    csv_name = model_name + '-subcase2.csv'  # hard code QQ
    GRAV = 9806.65
    csv_path = Path(cwd).joinpath(csv_name)
    df = pd.read_csv(csv_path)
    peak_freq, peak_acc = 0, 0
    for col in df.columns:
        if not col.startswith('Time'):
            max_acc = df[col].max() / GRAV
            max_idx = df[col].idxmax()
            if max_acc > peak_acc:
                peak_acc = max_acc
                peak_freq = df['Time'].iloc[max_idx]
    return peak_freq, peak_acc


def check_break_iteration(config: dict, peak: tuple[float, float], itr: int, logger: logging.Logger) -> bool:
    break_iteration = False
    if check_tolerance(config, peak, logger):
        logger.info('Converged!')
        break_iteration = True
    if itr > config['tunning']['iteration_limit']:
        logger.info('Reached the iteration limit.')
        break_iteration = True
    return break_iteration


def check_tolerance(config: dict, peak: tuple[float, float], logger: logging.Logger) -> bool:
    target = config['tunning']['target']
    tolerance = config['tunning']['tolerance_percentage']
    error = sum([abs((p-t)/t) for p, t in zip(peak, target)]) / 2 * 100
    logger.info(f'Error: {error:.3f}%')
    if error < tolerance:
        return True
    else:
        return False


def save_new_fem(config: dict, lines_ori: list[str], row_idx: int, damping: float, model_name: str):
    cwd = config['cwd']
    rubber_data_new = lines_ori[row_idx][0:64] + f'{damping:<8.5f}\n'
    lines_new = lines_ori.copy()
    lines_new[row_idx] = rubber_data_new
    fem_path = Path(cwd).joinpath(f'{model_name}.fem')
    with open(fem_path, 'w') as f:
        f.writelines(lines_new)


def find_new_damping(config: dict, damping_ori: float, peak_acc_ori: float, peak_acc_tmp: float, logger: logging.Logger) -> float:
    tgt_acc = config['tunning']['target'][-1]
    damping_delta = config['tunning']['damping_delta']
    error_acc_ori = peak_acc_ori - tgt_acc
    error_acc_tmp = peak_acc_tmp - tgt_acc
    slope = (error_acc_tmp - error_acc_ori) / damping_delta
    damping_new = damping_ori - (error_acc_ori / slope)
    logger.info(f'new damping: {damping_new:8.5f}\n')
    return damping_new


def get_new_model_name(model_name_ori: str, itr: int):
    suffix = f'-itr{itr:03d}'
    if itr == 1:
        model_name_new = model_name_ori + suffix
    else:
        model_name_new = model_name_ori[0:-len(suffix)] + suffix
    return model_name_new


def main():
    # Configurations
    config = read_configuration('config.json')
    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger()
    model_name = config['solve']['model_ini']
    damping_delta = config['tunning']['damping_delta']
    model_tmp = 'temp'

    # Parse initial *.fem 
    lines, row_idx = tick_fem(config, model_name)
    elastic, damping = retrieve_parameters(lines[row_idx])

    itr = 0
    while True:
        # Review current model
        logger.info(f'Iteration: {itr:2d}')
        logger.info(f'Elastic: {elastic:8.5f}, Damping: {damping:8.5f}')

        # Run current model
        peak = run_model(config, model_name, logger)
        if check_break_iteration(config, peak, itr, logger):
            break
        itr += 1

        # # Temp model
        # damping_tmp = damping + damping_delta
        # save_new_fem(config, lines, row_idx, damping_tmp, model_tmp)
        # peak_freq_tmp, peak_acc_tmp = run_model(config, model_tmp, logger)

        # # New model
        # damping_new = find_new_damping(
        #     config, damping, peak_acc, peak_acc_tmp, logger
        # )
        # model_name = get_new_model_name(model_name, itr)
        # save_new_fem(config, lines, row_idx, damping_new, model_name)
    logger.info('Done.')


if __name__ == '__main__':
    main()
