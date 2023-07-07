import math
from typing import List

import matplotlib.pyplot as plt


OUT_PATH = 'D:/my-analysis/type-m-subassy/test/type-m-subassy-frf.out'
TEXT_INI = 'MODAL EFFECTIVE MASS FRACTION FOR SUBCASE'
TEXT_END = 'SUBCASE TOTAL'


def tick_line_range(lines: List[str]) -> List[int]:
    for idx, line in enumerate(lines):
        if TEXT_INI in line:
            tick_ini = idx + 5
            break

    for idx, line in enumerate(lines[tick_ini:]):
        if TEXT_END in line:
            tick_end = tick_ini + idx - 1
            break
    return tick_ini, tick_end


def fetch_values_in_line(line: str) -> List[float]:
    vals = list(map(eval, line.split()))
    mode, freq, mass_x, mass_y, mass_z = vals[:5]
    return mode, freq, mass_x, mass_y, mass_z


def iter_lines(lines: List[str]) -> List[List[float]]:
    mode_arr, freq_arr, mass_x_arr, mass_y_arr, mass_z_arr = \
        [], [], [], [], []
    for line in lines:
        mode, freq, mass_x, mass_y, mass_z = \
            fetch_values_in_line(line)
        mode_arr.append(mode)
        freq_arr.append(freq)
        mass_x_arr.append(mass_x)
        mass_y_arr.append(mass_y)
        mass_z_arr.append(mass_z)
    return mode_arr, freq_arr, mass_x_arr, mass_y_arr, mass_z_arr


def fetch_modal_mass(out_path: str):
    with open(out_path, 'r') as f:
        lines = f.readlines()
    tick_ini, tick_end = tick_line_range(lines)
    valid_lines = lines[tick_ini:tick_end+1]
    return iter_lines(valid_lines)


def plot_distribution(freq_arr: List[float], mass_x_arr: List[float], mass_y_arr: List[float], mass_z_arr: List[float]):
    fig = plt.figure(figsize=(4, 2.4), tight_layout=True)
    ax = plt.axes()
    ax.stem(
        freq_arr, mass_x_arr,
        basefmt='tab:orange', linefmt='tab:orange', label='mass_x'
    )
    ax.stem(
        freq_arr, mass_y_arr,
        basefmt='tab:blue', linefmt='tab:blue', label='mass_y'
    )
    ax.stem(
        freq_arr, mass_z_arr,
        basefmt='tab:green', linefmt='tab:green', label='mass_z'
    )
    ax.set_xlabel('frequency, Hz')
    ax.set_ylabel('mass fraction')
    ax.set_title('Modal Mass Distribution')
    ax.legend()
    plt.show()


def create_freq2_arr(f1: float, f2: float, nf: int) -> List[float]:
    d = math.log(f2 / f1) / nf
    arr = [f1 * math.exp(itr * d) for itr in range(nf)]
    arr.append(f2)
    return arr


def main():
    mode_arr, freq_arr, mass_x_arr, mass_y_arr, mass_z_arr = \
        fetch_modal_mass(OUT_PATH)
    plot_distribution(freq_arr, mass_x_arr, mass_y_arr, mass_z_arr)
    freq2_arr = create_freq2_arr(1, 150, 6)


if __name__ == '__main__':
    main()
