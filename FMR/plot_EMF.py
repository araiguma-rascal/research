import matplotlib.pyplot as plt
import numpy as np
import pandas
import sys

def main():
    data = pandas.read_csv('181729-10GHz_300K_1mW_EMF.csv', usecols=['Magnetic (kG)', 'EMF (V)'], header=0)
    data['Magnetic (kG)'] *= 100
    data['EMF (V)'] *= 1e6

    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.figure(figsize=(6,4))
    fig, ax = plt.subplots()
    ax.set_xlabel(r"Magnetic Field (mT)", {'family': 'Times New Roman', 'size': 16})
    ax.set_ylabel(r"Electromotive Force ($\mu$V)", {'family': 'Times New Roman', 'size': 16})
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    ax.plot(data['Magnetic (kG)'], data['EMF (V)'])
    ax.text(182, -0.7, '5 GHz', size=16)
    ax.text(182, -0.75, '300 K', size=16)
    plt.show()

if __name__ == "__main__":
    main()