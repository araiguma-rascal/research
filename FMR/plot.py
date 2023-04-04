import matplotlib.pyplot as plt
import numpy as np
import pandas
import sys
import os
import re

class DataFMR:
    def __init__(self, freq_str, freq_int, data):
        self.freq_str = freq_str
        self.freq_int = freq_int
        self.data = data

def get_data():
    path = './'
    files = os.listdir(path)
    obj_array = []
    for filename in files:
        if '1mW.csv' in filename:
            data = pandas.read_csv(filename, usecols=['Magnetic Flux Density(kG)', 'Absorption Derivative'], header=0, skiprows=lambda x: x in range(1, 11))
            data['Magnetic Flux Density(kG)'] *= 100
            data = data.rename(columns={'Magnetic Flux Density(kG)': 'Magnetic Flux Density (mT)'})
            data = data.rename(columns={'Absorption Derivative': 'Absorption Derivative (a.u.)'})
            data['Absorption Derivative (a.u.)'] -= np.average(data['Absorption Derivative (a.u.)'])
            freq_int = int(get_freq(filename)[0:-3])
            obj_array.append(DataFMR(get_freq(filename) ,freq_int, data))
    return obj_array

def get_freq(string):
    pattern = r'\d{1,} GHz'
    result = re.search(pattern, string)
    return result.group(0)

def main():
    obj_array = get_data()
    obj_array = sorted(obj_array, key=lambda x: x.freq_int)
    obj_array = reversed(obj_array)

    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.figure(figsize=(6,4))
    fig, ax = plt.subplots()
    ax.set_xlabel(r"Magnetic Field (mT)", {'family': 'Times New Roman', 'size': 16})
    ax.set_xlim(0, 300)
    plt.xticks(fontsize=16)
    ax.set_ylabel(r"Absorption Derivative (a.u.)", {'family': 'Times New Roman', 'size': 16})
    cmap = plt.get_cmap("rainbow")

    for obj in obj_array:
        ax.plot(obj.data['Magnetic Flux Density (mT)'], obj.data['Absorption Derivative (a.u.)'], label=obj.freq_str, color=cmap(int((obj.freq_int-2)/(13-2)*cmap.N)))
    
    ax.set_yticks([])
    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=12)
    ax.text(10, 0.9, '300 K', size=16)

    plt.show()

if __name__ == "__main__":
    main()