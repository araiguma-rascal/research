import re
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas


MAXFEV = 10000  # フィッティングの繰り返し上限


# constructer for FMR data
class DataFMR:
    def __init__(self, data, filename, **kwards):
        self.data = data
        self.filename = filename
        self.temperature_str = kwards['temperature_str'] if 'temperature_str' in kwards.keys(
        ) else None
        self.temperature_num = kwards['temperature_num'] if 'temperature_num' in kwards.keys(
        ) else None
        self.freq_str = kwards['freq_str'] if 'freq_str' in kwards.keys(
        ) else None
        self.freq_num = kwards['freq_num'] if 'freq_num' in kwards.keys(
        ) else None
        self.sign = kwards['sign'] if 'sign' in kwards.keys(
        ) else None
        self.result = kwards['result'] if 'result' in kwards.keys(
        ) else None


# get data from the file path and the column names
def get_data(path, filename, cols):
    data = pandas.read_csv(
        path + filename, usecols=cols, header=0, skiprows=lambda x: x in range(1, 50), skipfooter=10, engine='python')

    # get condition parameters
    temperature_str = get_param(filename, 'K')
    temperature_num = str2num(temperature_str)
    freq_str = get_param(filename, 'GHz')
    freq_num = str2num(freq_str)

    obj = DataFMR(data, filename, temperature_str=temperature_str,
                  temperature_num=temperature_num, freq_str=freq_str, freq_num=freq_num)
    return obj


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


# main fuction
def main():
    # get data
    obj = get_data('../', '20220118-224515-X796n2n1_285K_14GHz_-10dBm_0deg_perp_0V.csv',
                   ['Magnetic Field (kG)', 'EMF (V)'])
    fig = plt.figure()
    result = pandas.DataFrame(index=[], columns=[
                              'Temperature (K)', 'Frequency (GHz)', 'Sign', 'a0', 'a1', 'a2', 'V_sym', 'delta_H', 'H_res', 'V_AHE'])

    # modify data
    obj.data['Magnetic Field (mT)'] = obj.data['Magnetic Field (kG)'] * 100
    obj.data['Magnetic Field (T)'] = obj.data['Magnetic Field (mT)'] * 1e-3
    obj.sign = 'Negative' if '_gyakujiba.csv' in obj.filename else 'Positive'

    # fitting
    estimation_ini = [
        0, 0, 0, -1e-6, 1, -300, 10e-6] if '_gyakujiba.csv' in obj.filename else [0, 0, 0, 1e-6, 1, 300, 10e-6]
    params = fitting(
        spin_pomp, obj.data['Magnetic Field (mT)'], obj.data['EMF (V)'], estimation_ini)
    obj.data['EMF_fit (V)'] = spin_pomp(
        obj.data['Magnetic Field (mT)'], *params)
    obj.result = [obj.temperature_num,
                  obj.freq_num, obj.sign] + list(params)
    obj.result = pandas.DataFrame([obj.result], columns=result.columns)
    result = pandas.concat([result, obj.result])

    # plot
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(obj.freq_str)
    ax.plot(obj.data['Magnetic Field (mT)'], obj.data['EMF_fit (V)'])
    ax.plot(obj.data['Magnetic Field (mT)'], obj.data['EMF (V)'])

    print(result)
    data2csv(result, './', 'result_FMR_volt.csv')
    plt.show()

    return


# fitting
def fitting(func, x, y, estimation_ini):
    params, _ = curve_fit(func, x, y, p0=estimation_ini, maxfev=MAXFEV)
    return params


# function for spin-pomping voltage
def spin_pomp(x, a0, a1, a2, V_sym, delta_H, H_res, V_AHE):
    return a0 + a1*x + a2*x**2 +\
        V_sym * delta_H**2 / ((x - H_res)**2 + delta_H**2) + \
        V_AHE * -2 * delta_H * (x-H_res) / ((x-H_res)**2 + delta_H**2)


if __name__ == '__main__':
    main()
