import matplotlib.pyplot as plt
import numpy as np
import pandas
import sys
import os
import re

bohr_magnetization = 9.2740100783e-24
dirac_const = 6.62607004E-34 / (2*np.pi)
g_factor = 1.95
gyromagnetic_ratio = g_factor * bohr_magnetization / dirac_const
H_0 = 0.746704067 # mT

class DataFMR:
    def __init__(self, temperature_str, temperature_int, data, damping_const=None):
        self.temperature_str = temperature_str
        self.temperature_int = temperature_int
        self.data = data
        self.damping_const = damping_const


def get_data():
    path = './'
    files = os.listdir(path)
    obj_array = []
    for filename in files:
        if '.csv' in filename:
            data = pandas.read_csv(filename, usecols=[
                                   'Magnetic Flux Density(kG)', 'S21 (dB)'], header=0, skiprows=lambda x: x in range(1, 11))
            data['Magnetic Flux Density(kG)'] *= 100
            data = data.rename(
                columns={'Magnetic Flux Density(kG)': 'Magnetic Flux Density (mT)'})
            data['Absorption Derivative (a.u.)'] = -np.gradient(
                data['S21 (dB)'], data['Magnetic Flux Density (mT)'])
            data['Absorption Derivative (a.u.)'] -= np.average(
                data['Absorption Derivative (a.u.)'])
            tmp = int(get_temperature(filename)[0:-1])
            data['Absorption Derivative (a.u.)'] += (tmp-30)*0.001
            obj_array.append(DataFMR(get_temperature(filename), tmp, data))
    return obj_array


def get_temperature(string):
    pattern = r'\d{1,}K'
    result = re.search(pattern, string)
    return result.group(0)


def main():
    obj_array = get_data()
    obj_array = sorted(obj_array, key=lambda x: x.temperature_int)
    obj_array = reversed(obj_array)

    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.figure(figsize=(6, 4))
    plt.subplots_adjust(left=0.1, right=0.95, bottom=0, top=0.1)
    fig, ax = plt.subplots()
    ax.set_xlabel(r"Temperature (K)", {'family': 'Times New Roman', 'size': 16})
    plt.xticks(fontsize=16)
    ax.set_ylabel(r"Damping Constant", {'family': 'Times New Roman', 'size': 16})
    cmap = plt.get_cmap("rainbow")

    temp, damping_const = [], []
    for obj in obj_array:
        argmin, argmax = np.argmin(obj.data['Absorption Derivative (a.u.)']), np.argmax(obj.data['Absorption Derivative (a.u.)'])
        linewidth = obj.data['Magnetic Flux Density (mT)'][argmin] - obj.data['Magnetic Flux Density (mT)'][argmax]
        slope = ((linewidth - H_0)*0.001/1.25663706) / 5e9
        obj.damping_const = slope * gyromagnetic_ratio / (2*np.pi)
        damping_const.append(obj.damping_const)
        temp.append(obj.temperature_int)
        print(obj.temperature_str, linewidth, obj.damping_const)
    plt.plot(temp, damping_const)
    #plt.legend(bbox_to_anchor=(1.01, 1.05), loc='upper left')

    plt.show()


if __name__ == "__main__":
    main()
