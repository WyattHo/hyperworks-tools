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
    arr = [round(f1 * math.exp(itr * d), 3) for itr in range(nf)]
    arr.append(f2)
    return arr


def sign(val: float):
    if val > 0:
        return 1
    elif val < 0:
        return -1
    elif val == 0:
        return 0


def get_subrange_frequencies(freq_ini: float, freq_end: float, nef: int, cluster: float):
    fk_arr = []
    for k in range(nef):
        zeta = -1 + 2 * k / (nef - 1)
        fk = 0.5 * (freq_ini + freq_end) + 0.5 * (freq_end - freq_ini) * abs(zeta)**(1/cluster) * sign(zeta)
        fk_arr.append(round(fk, 3))
    return fk_arr


def create_freq3_arr(modal_f_arr: List[float], f1: float, f2: float, nef: int, cluster: float) -> List[float]:
    trimmed_arr = modal_f_arr.copy()
    for val in modal_f_arr:
        if (val <= f1) or (val >= f2):
            trimmed_arr.remove(val)
    
    trimmed_arr.sort()
    trimmed_arr.insert(0, f1)
    trimmed_arr.append(f2)
    
    freq3_set = set([])
    for idx in range(len(trimmed_arr)-1):
        freq_ini = trimmed_arr[idx]
        freq_end = trimmed_arr[idx+1]
        subrange_freqs = get_subrange_frequencies(freq_ini, freq_end, nef, cluster)
        freq3_set.update(subrange_freqs)
    
    freq3_arr = list(freq3_set)
    freq3_arr.sort()
    return freq3_arr


def main():
    mode_arr, freq_arr, mass_x_arr, mass_y_arr, mass_z_arr = \
        fetch_modal_mass(OUT_PATH)
    freq2_arr = create_freq2_arr(1, 150, 6)
    freq3_arr = create_freq3_arr(freq_arr, 150, 600, 5, 2.0)
    freq_all = list(set(freq2_arr + freq3_arr))
    freq_all.sort()
    plot_distribution(freq_arr, mass_x_arr, mass_y_arr, mass_z_arr)


if __name__ == '__main__':
    main()
