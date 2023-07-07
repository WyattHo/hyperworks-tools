from typing import List

from matplotlib import pyplot as plt


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


def fetch_values_in_line(line: str):
    vals = list(map(eval, line.split()))
    mode, freq, mass_x, mass_y, mass_z = vals[:5]
    return mode, freq, mass_x, mass_y, mass_z


def iter_lines(lines: List[str]):
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


def main():
    mode_arr, freq_arr, mass_x_arr, mass_y_arr, mass_z_arr = \
        fetch_modal_mass(OUT_PATH)


if __name__ == '__main__':
    main()