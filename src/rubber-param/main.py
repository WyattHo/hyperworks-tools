import json
import logging
import logging.config
import numpy as np
import pandas as pd
import subprocess
from pathlib import Path


def read_configuration(config_name: str) -> dict:
    this_dir = Path(__file__).parent
    config_path = this_dir.joinpath(config_name)
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def read_fem(config: dict, model_name: str) -> list[str]:
    cwd = config['cwd']
    fem = model_name + '.fem'
    with open(Path(cwd).joinpath(fem), 'r') as f:
        lines = f.readlines()
    return lines


def tick_fem(config: dict, lines: list[str]) -> int:
    prefix = config['parser']['prefix']
    rubber_name = config['parser']['rubber_name']
    for row_idx, line in enumerate(lines):
        if line.startswith(prefix) and rubber_name in line:
            break
    return row_idx


def retrieve_parameters(config: dict, lines: list[str], row_idx: int) -> tuple[float, float]:
    line_inc_elastic = config['parser']['line_increment']['elastic']
    line_inc_damping = config['parser']['line_increment']['damping']
    field_len = config['parser']['field_length']
    field_idx_elastic = config['parser']['field_idx']['elastic']
    field_idx_damping = config['parser']['field_idx']['damping']

    line_elastic = lines[row_idx + line_inc_elastic]
    line_damping = lines[row_idx + line_inc_damping]

    str_elastic = field_len * field_idx_elastic - field_len
    end_elastic = field_len * field_idx_elastic
    str_damping = field_len * field_idx_damping - field_len
    end_damping = field_len * field_idx_damping

    elastic = float(line_elastic[str_elastic:end_elastic])
    damping = float(line_damping[str_damping:end_damping])
    return elastic, damping


def review_current_model(itr: int, params: list[float], logger: logging.Logger):
    elastic, damping = params
    logger.info(f'Iteration: {itr:2d}')
    logger.info(f'Elastic: {elastic:8.5f}, Damping: {damping:8.5f}')


def run_model(config: dict, model_name: str, logger: logging.Logger) -> tuple[float, float]:
    run_solver(config, model_name, logger)
    postprocess_h3d(config, model_name, logger)
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
    subcase_indices = ','.join([f'{idx}' for idx in config['export']['subcase_indices']])
    result_types = ','.join([f'{idx}' for idx in config['export']['result_types']])
    result_components = '\",\"'.join([f'{idx}' for idx in config['export']['result_components']])
    result_names = ','.join([f'{idx}' for idx in config['export']['result_names']])

    h3d_path = Path(cwd).joinpath(h3d_name)
    tcl_path = Path(__file__).parent.joinpath(tcl_name)

    cmd = f'hw -tcl {tcl_path} {h3d_path} {nodes} {subcase_indices} \"{result_types}\" \"{result_components}\" {result_names}'
    logger.info(f'Executing: {tcl_path}')
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)


def read_csv_data(config: dict, model_name: str) -> tuple[float, float]:
    cwd = config['cwd']
    subcase_idx = config['tunning']['peak']['subcase_idx']
    result_name = config['tunning']['peak']['result_name']

    csv_name = model_name + f'-subcase{subcase_idx:02d}-{result_name}.csv'
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


def replace_field_value(line_ori: str, field_idx: int, field_len: int, value: float):
    tick_str = field_len * field_idx - field_len
    tick_end = field_len * field_idx
    value_string = f'{value:<8.5f}'
    if len(value_string) > 8:
        value_string = value_string[:8]
    return line_ori[:tick_str] + value_string + line_ori[tick_end:]


def save_new_fem(config: dict, lines_ori: list[str], row_idx: int, params: list[float], model_name: str):
    cwd = config['cwd']
    line_inc_elastic = config['parser']['line_increment']['elastic']
    line_inc_damping = config['parser']['line_increment']['damping']
    field_len = config['parser']['field_length']
    field_idx_elastic = config['parser']['field_idx']['elastic']
    field_idx_damping = config['parser']['field_idx']['damping']
    elastic, damping = params

    line_elastic = lines_ori[row_idx + line_inc_elastic]
    line_damping = lines_ori[row_idx + line_inc_damping]

    lines_new = lines_ori.copy()
    if line_inc_elastic == line_inc_damping:
        line_elastic = replace_field_value(line_elastic, field_idx_elastic, field_len, elastic)
        line_damping = replace_field_value(line_elastic, field_idx_damping, field_len, damping)
        lines_new[row_idx + line_inc_damping] = line_damping + '\n'
    else:
        line_elastic = replace_field_value(line_elastic, field_idx_elastic, field_len, elastic)
        line_damping = replace_field_value(line_damping, field_idx_damping, field_len, damping)
        lines_new[row_idx + line_inc_elastic] = line_elastic
        lines_new[row_idx + line_inc_damping] = line_damping + '\n'

    fem_path = Path(cwd).joinpath(f'{model_name}.fem')
    with open(fem_path, 'w') as f:
        f.writelines(lines_new)


def find_new_params(config: dict, peak: tuple[float, float], peak_dx1: tuple[float, float], peak_dx2: tuple[float, float], params: tuple[float, float]) -> list[float]:
    dx1, dx2 = config['tunning']['delta']
    freq_tgt, acc_tgt = config['tunning']['target']
    freq_ori, acc_ori = peak
    freq_dx1, acc_dx1 = peak_dx1
    freq_dx2, acc_dx2 = peak_dx2

    diff_11 = (freq_dx1 - freq_ori) / dx1
    diff_12 = (freq_dx2 - freq_ori) / dx2
    diff_21 = (acc_dx1 - acc_ori) / dx1
    diff_22 = (acc_dx2 - acc_ori) / dx2
    diff_mat = np.array([[diff_11, diff_12], [diff_21, diff_22]])

    error_freq = freq_ori - freq_tgt
    error_acc = acc_ori - acc_tgt
    error_mat = np.array([error_freq, error_acc]).reshape((2, 1))

    diff_mat_inv = np.linalg.inv(diff_mat)
    params_new = np.array(params).reshape((2, 1)) - diff_mat_inv.dot(error_mat)
    return [p if p > 0 else 0 for p in params_new.flatten().tolist()]


def get_new_model_name(model_name_ori: str, itr: int):
    suffix = f'-itr{itr + 1:03d}'
    if itr == 0:
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
    dx1, dx2 = config['tunning']['delta']

    # Parse initial *.fem
    lines = read_fem(config, model_name)
    row_idx = tick_fem(config, lines)
    params = retrieve_parameters(config, lines, row_idx)

    itr = 0
    while True:
        # Current model
        review_current_model(itr, params, logger)
        peak = run_model(config, model_name, logger)
        if check_break_iteration(config, peak, itr, logger):
            break

        # Temp model
        params_tmp = [params[0] + dx1, params[1]]
        save_new_fem(config, lines, row_idx, params_tmp, 'temp-1')
        peak_dx1 = run_model(config, 'temp-1', logger)

        params_tmp = [params[0], params[1] + dx2]
        save_new_fem(config, lines, row_idx, params_tmp, 'temp-2')
        peak_dx2 = run_model(config, 'temp-2', logger)

        # New model
        params = find_new_params(config, peak, peak_dx1, peak_dx2, params)
        model_name = get_new_model_name(model_name, itr)
        save_new_fem(config, lines, row_idx, params, model_name)
        itr += 1

    logger.info('Done.')


if __name__ == '__main__':
    main()
