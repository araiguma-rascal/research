from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np
import pandas
import os
import re


# constructer for FMR data
class DataFMR:
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
        self.sign = kwards['sign'] if 'sign' in kwards.keys(
        ) else None
        self.result = kwards['result'] if 'result' in kwards.keys(
        ) else None


# get data from the file path and the column names
def get_data(path, cols):
    files = os.listdir(path)
    obj_array = []
    for filename in files:
        print(filename)
        if '.csv' in filename:
            data = pandas.read_csv(
                path + filename, usecols=cols, header=0, skiprows=lambda x: x in range(1, 101), engine='python')
            # get condition parameters
            temperature_str = get_param(filename, 'K')
            temperature_num = str2num(temperature_str)
            gate_volt_str = get_param(filename, 'V')
            gate_volt_num = str2num(gate_volt_str)

            obj_array.append(DataFMR(data, filename, temperature_str=temperature_str,
                                     temperature_num=temperature_num, gate_volt_str=gate_volt_str, gate_volt_num=gate_volt_num))
    return obj_array


# get a parameter from a string and the corresponding unit
def get_param(string, unit):
    pattern = r'[-]?[0-9]+' + unit
    param = re.search(pattern, string).group(0)
    return param


# write date into a csv file
def data2csv(data, path, filename):
    return data.to_csv(path+filename, index=False)


def str2num(string):
    pattern = r'[-]?[0-9]+'
    param = re.search(pattern, string).group(0)
    return float(param)


def get_rowscols(num):
    rows, cols = (0, 0)
    sqrt = int(np.sqrt(num))
    if num <= sqrt**2:
        rows, cols = (sqrt, sqrt)
    elif num <= sqrt * (sqrt+1):
        rows, cols = (sqrt, sqrt+1)
    else:
        rows, cols = (sqrt+1, sqrt+1)
    return rows, cols


# main fuction
def main():
    # get data
    obj_array = get_data('../', ['Magnetic Field (kG)', 'EMF (V)'])
    obj_array = sorted(obj_array, key=lambda x: x.filename)
    fig = plt.figure()
    rows, columns = get_rowscols(len(obj_array))
    result = pandas.DataFrame(index=[], columns=[
                              'Temperature (K)', 'Gate Voltage (V)', 'Sign', 'a0', 'a1', 'a2', 'V_sym', 'delta_H', 'H_res', 'V_AHE'])

    for i, obj in enumerate(obj_array):

        # modify data
        obj.data['Magnetic Field (mT)'] = obj.data['Magnetic Field (kG)'] * 100
        obj.data['Magnetic Field (T)'] = obj.data['Magnetic Field (mT)'] * 1e-3
        obj.sign = 'Negative' if '_r.csv' in obj.filename else 'Positive'

        # fitting
        estimation_ini = [
            0, 0, 0, 0, 4, -90, 10e-6] if '_r.csv' in obj.filename else [0, 0, 0, 0, 4, 90, 10e-6]
        try:
            params = fitting(
                spin_pomp, obj.data['Magnetic Field (mT)'], obj.data['EMF (V)'], estimation_ini)
        except RuntimeError:
            print("Optimization Failed!!!")
            params = [
                0, 0, 0, 0, 4, -90, 10e-6] if '_r.csv' in obj.filename else [0, 0, 0, 0, 4, 90, 10e-6]
        obj.data['EMF_fit (V)'] = spin_pomp(
            obj.data['Magnetic Field (mT)'], *params)
        obj.result = [obj.temperature_num,
                      obj.gate_volt_num, obj.sign] + list(params)
        obj.result = pandas.DataFrame([obj.result], columns=result.columns)
        print(obj.result)
        result = pandas.concat([result, obj.result])

        # plot
        ax = fig.add_subplot(rows, columns, i+1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(obj.gate_volt_str)
        ax.plot(obj.data['Magnetic Field (mT)'], obj.data['EMF_fit (V)'])
        ax.plot(obj.data['Magnetic Field (mT)'], obj.data['EMF (V)'])

    print(result)
    data2csv(result, './', 'result_FMR_volt.csv')
    plt.show()

    return


# fitting
def fitting(func, x, y, estimation_ini):
    params, _ = curve_fit(func, x, y, p0=estimation_ini, maxfev=10000)
    return params


# function for spin-pomping voltage
def spin_pomp(x, a0, a1, a2, V_sym, delta_H, H_res, V_AHE):
    return a0 + a1*x + a2*x**2 +\
        V_sym * delta_H**2 / ((x - H_res)**2 + delta_H**2) + \
        V_AHE * -2 * delta_H * (x-H_res) / ((x-H_res)**2 + delta_H**2)


if __name__ == '__main__':
    main()
