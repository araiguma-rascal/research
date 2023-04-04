import matplotlib.pyplot as plt
import numpy as np
import pandas
import sys
import os
import re


class DataFMR:
    def __init__(self, temperature_str, temperature_int, data):
        self.temperature_str = temperature_str
        self.temperature_int = temperature_int
        self.data = data


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
    fig, ax = plt.subplots()
    ax.set_xlabel(r"Magnetic Field (mT)", {'family': 'Times New Roman', 'size': 16})
    ax.set_xlim(0, 70)
    plt.xticks(fontsize=16)
    ax.set_ylabel(r"Absorption Derivative (a.u.)", {'family': 'Times New Roman', 'size': 16})

    cmap = plt.get_cmap("rainbow")
    for obj in obj_array:
        ax.plot(obj.data['Magnetic Flux Density (mT)'], obj.data['Absorption Derivative (a.u.)'],
                label=obj.temperature_str, color=cmap(int((obj.temperature_int-30)/(300-30)*cmap.N)))
        if obj.temperature_int in [300, 265]:
            ax.text(np.min(obj.data['Magnetic Flux Density (mT)'])-3, np.average(obj.data['Absorption Derivative (a.u.)']), obj.temperature_str, size=16, horizontalalignment='right', verticalalignment='center', color=cmap(int((obj.temperature_int-30)/(300-30)*cmap.N)))
        elif obj.temperature_int in [250, 200, 150, 100, 50, 30]:
            ax.text(np.max(obj.data['Magnetic Flux Density (mT)'])+3, np.average(obj.data['Absorption Derivative (a.u.)']), obj.temperature_str, size=16, horizontalalignment='left', verticalalignment='center', color=cmap(int((obj.temperature_int-30)/(300-30)*cmap.N)))

    ax.set_yticks([])
    #plt.legend(bbox_to_anchor=(1.01, 1.05), loc='upper left')
    ax.text(2, 0.26, '5 GHz', size=16)

    plt.show()


if __name__ == "__main__":
    main()
