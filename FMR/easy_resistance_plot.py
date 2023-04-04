''' 抵抗値を簡単にプロットするプログラム '''
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas


# constructer for FMR data
class DataObj:
    def __init__(self, data, filename, **kwards):
        self.data = data
        self.filename = filename
        self.temperature_str = kwards['temperature_str'] if 'temperature_str' in kwards.keys(
        ) else None
        self.temperature_num = kwards['temperature_num'] if 'temperature_num' in kwards.keys(
        ) else None
        self.gate_volt_str = kwards['gate_volt_str'] if 'gate_volt_str' in kwards.keys(
        ) else None
        self.gate_volt_num = kwards['gate_volt_num'] if 'gate_volt_num' in kwards.keys(
        ) else None
        self.go_back = kwards['go_back'] if 'go_back' in kwards.keys(
        ) else None


# get data from the file path and the column names
def get_data(path):
    files = os.listdir(path)
    obj_array = []
    for filename in files:
        if '.csv' in filename:
            data = pandas.read_csv(
                path + filename, engine='python', names=["I (A)", "V (V)"])
            obj = DataObj(data, filename)

            # get condition parameters
            obj.gate_volt_str = get_param(filename, 'V')
            obj.gate_volt_num = str2num(obj.gate_volt_str)
            obj.go_back = get_go_back(filename)

            obj_array.append(obj)
    return obj_array


# get a parameter from a string and the corresponding unit
def get_param(string, unit):
    pattern = r'[-]?[0-9]+' + unit
    param = re.search(pattern, string).group(0)
    return param


def str2num(string):
    pattern = r'[-]?[0-9]+'
    param = re.search(pattern, string).group(0)
    return float(param)


def get_go_back(string):
    pattern = r'No[1-2]+'
    param = re.search(pattern, string).group(0)
    return param


# write date into a csv file
def data2csv(data, path, filename):
    return data.to_csv(path+filename, index=False)


# main fuction
def main():
    # get data
    obj_array = get_data('../')
    color_list = ['g', 'b']
    for i in range(2):
        ind = i+1
        data_array = [obj for obj in obj_array if obj.go_back ==
                      'No{}'.format(ind)]
        data_array = sorted(data_array, key=lambda x: x.gate_volt_num)
        res_array = []
        volt_array = []
        for obj in data_array:

            resistance, _ = np.polyfit(
                obj.data["I (A)"], obj.data["V (V)"], 1)
            res_array.append(resistance)
            volt_array.append(obj.gate_volt_num)

        # plot
        plt.plot(volt_array, res_array, color=color_list[i])

    plt.show()


if __name__ == '__main__':
    main()
