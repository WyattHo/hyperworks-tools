import math
from typing import List

import matplotlib.pyplot as plt
import pandas as pd


OUT_PATH = 'D:/my-analysis/type-m-subassy/test/type-m-subassy-frf.out'
TEXT_INI = 'MODAL EFFECTIVE MASS FRACTION FOR SUBCASE'
TEXT_END = 'SUBCASE TOTAL'
Table = List[List[float]]


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


def iter_lines(lines: List[str]) -> Table:
    table = []
    for line in lines:
        values = fetch_values_in_line(line)
        table.append(values)
    return table


def fetch_modal_mass(out_path: str) -> pd.DataFrame:
    with open(out_path, 'r') as f:
        lines = f.readlines()
    tick_ini, tick_end = tick_line_range(lines)
    valid_lines = lines[tick_ini:tick_end+1]
    table = iter_lines(valid_lines)
    columns = ['mode num', 'frequency', 'mass_x', 'mass_y', 'mass_z']
    df = pd.DataFrame(data=table, columns=columns)
    return df


def plot_mass_distribution(freq_arr: List[float], mass_x_arr: List[float], mass_y_arr: List[float], mass_z_arr: List[float]):
    fig = plt.figure(figsize=(6, 2.1), tight_layout=True)
    ax = plt.axes()
    ax.plot(
        freq_arr, mass_x_arr, label='mass_x',
        linestyle='',
        marker='o',
        markerfacecolor=[1.0, 1.0, 1.0, 0.0],
        markeredgecolor='tab:blue'
    )
    ax.plot(
        freq_arr, mass_y_arr, label='mass_y',
        linestyle='', marker='x'
    )
    ax.plot(
        freq_arr, mass_z_arr, label='mass_z',
        linestyle='', marker='+'
    )
    ax.set_title('Modal Mass Distribution')
    ax.set_ylabel('mass fraction')
    ax.set_xlabel('frequency, Hz')
    ax.grid(visible=True, axis='both')
    ax.legend()
    plt.show()


def create_freqs_type2(f1: float, f2: float, nf: int) -> List[float]:
    d = math.log(f2 / f1) / nf
    freqs = [round(f1 * math.exp(itr * d), 3) for itr in range(nf)]
    freqs.append(f2)
    return freqs


def sign(val: float) -> int:
    if val > 0:
        return 1
    elif val < 0:
        return -1
    elif val == 0:
        return 0


def get_subrange(freq_ini: float, freq_end: float, nef: int, cluster: float):
    freqs = []
    for k in range(nef):
        zeta = -1 + 2 * k / (nef - 1)
        fk = 0.5 * (freq_ini + freq_end) \
            + 0.5 * (freq_end - freq_ini) * abs(zeta)**(1/cluster) * sign(zeta)
        freqs.append(round(fk, 3))
    return freqs


def create_freqs_type3(modal_f_arr: List[float], f1: float, f2: float, nef: int, cluster: float) -> List[float]:
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
        subrange = get_subrange(freq_ini, freq_end, nef, cluster)
        freq3_set.update(subrange)

    freq3_arr = list(freq3_set)
    freq3_arr.sort()
    return freq3_arr


def plot_modal_and_excitation_frequencies(freqs_modal, freqs_excite):
    fig = plt.figure(figsize=(8, 1.6), tight_layout=True)
    ax = plt.axes()
    ax.vlines(
        x=freqs_modal, ymin=0.0, ymax=1.0, label='modal',
        colors='tab:orange', linewidth=0.8
    )
    ax.vlines(
        x=freqs_excite, ymin=-1.0, ymax=0.0, label='excitation', 
        colors='tab:green', linewidth=0.8
    )
    ax.set_ybound(lower=-1.0, upper=1.0)
    ax.set_xlim([0, 700])
    ax.set_xlabel('frequency, Hz')
    ax.set_title('Range of frequency')
    ax.set_yticks([])
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.show()


def get_excitation_frequency(freqs_modal: List[float]):
    F1_TYPE2, F2_TYPE2, NF_TYPE2 = 1, 150, 6
    F1_TYPE3, F2_TYPE3, NEF_TYPE3, CLUSTER_TYPE3 = 150, 600, 5, 2.0
    freqs_type_2 = create_freqs_type2(
        F1_TYPE2, F2_TYPE2, NF_TYPE2
    )
    freqs_type_3 = create_freqs_type3(
        freqs_modal, F1_TYPE3, F2_TYPE3,
        NEF_TYPE3, CLUSTER_TYPE3
    )
    freqs_excite = list(set(freqs_type_2 + freqs_type_3))
    freqs_excite.sort()
    return freqs_excite


def main():
    df = fetch_modal_mass(OUT_PATH)
    freqs_modal = df['frequency']
    masses_x, masses_y, masses_z = df['mass_x'], df['mass_y'], df['mass_z']

    freqs_excite = get_excitation_frequency(freqs_modal.to_list())
    plot_mass_distribution(freqs_modal, masses_x, masses_y, masses_z)
    plot_modal_and_excitation_frequencies(freqs_modal, freqs_excite)


if __name__ == '__main__':
    main()