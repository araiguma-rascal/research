import pandas
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


class SquidMH:
    def __init__(self, data, filename):
        self.data = data  # pandasデータ
        self.filename = filename  # string

    def fitting(self, func, x_name, y_name, p0):
        params, _ = curve_fit(
            func, self.data[x_name], self.data[y_name], p0, maxfev=10000)
        return params


# fitting
def fitting(func, x, y, estimation_ini):
    params, _ = curve_fit(func, x, y, p0=estimation_ini, maxfev=10000)
    return params


def read_squid_file(path, filename):
    ind = 0
    with open(path+filename) as f:
        for ind, line in enumerate(f):
            if '[Data]' in line:
                break
    data = pandas.read_csv(path+filename,
                           skiprows=ind+1, header=0)
    return data


def main():
    EMU2MUB = 1.078283e20  # mu_B/emu
    area = 1.121e-2  # cm^2
    d = 3.88e-8 * 30  # cm
    volume = area * d  # cm^3
    LSMO_unit_volume = 3.88e-8**3  # cm^3

    # ファイル読み込み
    palladium = read_squid_file('raw/', 'Pd_MH_finever2.csv')
    data = read_squid_file('raw/', 'X918_LSMO-SiO2-Si_axis100_MH_300K.dat')

    # 磁場校正
    data['Calibrated Magnetic Field (Oe)'] = palladium['Calibrated Magnetic Field (Oe)']

    # 反or常磁性排除
    a, b = np.polyfit(
        data['Calibrated Magnetic Field (Oe)'][4:30], data['Moment (emu)'][4:30], 1)
    print(a, b)
    data['Moment of Ferromagnet (emu)'] = data['Moment (emu)'] - \
        a * data['Calibrated Magnetic Field (Oe)']

    # 磁場を上下対称化(平均とって引き算)
    data['Moment of Ferromagnet (emu)'] -= np.average(
        data['Moment of Ferromagnet (emu)'])

    # 単位変換
    data['Moment of Ferromagnet (emu/cm^3)'] = data['Moment of Ferromagnet (emu)'] / volume
    data['Moment of Ferromagnet (mu_B/Mn)'] = data['Moment of Ferromagnet (emu)'] * \
        EMU2MUB / (volume / LSMO_unit_volume)
    data['Calibrated Magnetic Field (T)'] = data['Calibrated Magnetic Field (Oe)'] / 10000

    # plot
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    fig = plt.figure()

    # 生データプロット
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(data['Calibrated Magnetic Field (T)'],
             data['Moment (emu)'])
    ax1.set_xlabel('Magnetic Field (T)')
    ax1.set_ylabel('Moment (emu)')
    # 補正後 emuプロット
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(data['Calibrated Magnetic Field (T)'],
             data['Moment of Ferromagnet (emu)'])
    ax2.set_xlabel('Magnetic Field (T)')
    ax2.set_ylabel('Moment of Ferromagnet(emu)')
    # emu/cm^3 プロット
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(data['Calibrated Magnetic Field (T)'],
             data['Moment of Ferromagnet (emu/cm^3)'])
    ax3.set_xlabel('Magnetic Field (T)')
    ax3.set_ylabel(r'Moment (emu/$cm^3$)')
    # mu_B/Mn プロット
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(data['Calibrated Magnetic Field (T)'],
             data['Moment of Ferromagnet (mu_B/Mn)'])
    ax4.set_xlabel('Magnetic Field (T)')
    ax4.set_ylabel(r'Moment ($\mu_B$/Mn)')

    # データ保存
    data.to_csv('analyzed/X918_LSMO-SiO2-Si_axis100_MH_300K.csv')

    # 全体プロット
    plt.show()


main()
