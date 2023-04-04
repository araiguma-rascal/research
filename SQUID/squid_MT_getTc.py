import pandas
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, peak_widths
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


def gradient_peaks(data):
    peaks, _ = find_peaks(data)
    peak_widths_indcs = peak_widths(data, peaks, rel_height=1)
    boroadest_peak = peaks[peak_widths_indcs[0].argmax()]
    return boroadest_peak


def smooth(data):
    window = 10  # 移動平均の範囲
    w = np.ones(window)/window
    return np.convolve(data, w, mode='same')


def tangent_line(x0, y0, grad):
    print(x0, y0, grad)
    x = np.linspace(x0-y0/grad, x0-y0/grad-50, 100)
    y = grad*(x-x0) + y0
    print(f"x切片は{x0-y0/grad}")
    return x, y


def main():
    EMU2MUB = 1.078283e20  # mu_B/emu
    area = 1.121e-2  # cm^2
    d = 3.88e-8 * 30  # cm
    volume = area * d  # cm^3
    LSMO_unit_volume = 3.88e-8**3  # cm^3

    # ファイル読み込み
    data = read_squid_file(
        'raw/', 'X918_LSMO-SiO2-Si_axis100_MT_5-400K_400Oe.dat')

    # 反or常磁性排除
    data['Moment of Ferromagnet (emu)'] = data['Moment (emu)'] - \
        np.mean(data['Moment (emu)'][-100:])  # MHが無いのでそのままとして仮定

    # 単位変換
    data['Moment of Ferromagnet (emu/cm^3)'] = data['Moment of Ferromagnet (emu)'] / volume
    data['Moment of Ferromagnet (mu_B/Mn)'] = data['Moment of Ferromagnet (emu)'] * \
        EMU2MUB / (volume / LSMO_unit_volume)

    data['Moment (emu/cm^3)'] = data['Moment (emu)'] / volume
    data['Moment (mu_B/Mn)'] = data['Moment (emu)'] * \
        EMU2MUB / (volume / LSMO_unit_volume)

    # 最大の傾き導出
    dM = np.gradient(data['Moment of Ferromagnet (mu_B/Mn)'])
    dT = np.gradient(data['Temperature (K)'])
    dMdT = dM/dT
    dMdT = smooth(dMdT)
    peak_ind = gradient_peaks(-dMdT)

    # plot
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    fig = plt.figure()

    # 生データemuプロット
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(data['Temperature (K)'],
             data['Moment (emu)'])
    ax1.set_xlabel('Temperature (K)')
    ax1.set_ylabel('Moment (emu)')

    # 傾きプロット
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(data['Temperature (K)'],
             dMdT)
    ax2.plot(data['Temperature (K)'][peak_ind], dMdT[peak_ind], 'x')
    ax2.set_xlabel('Temperature (K)')
    ax2.set_ylabel(r'dM/dT')

    # 処理後emu/cm^3プロット
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(data['Temperature (K)'],
             data['Moment of Ferromagnet (emu/cm^3)'])
    ax3.set_xlabel('Temperature (K)')
    ax3.set_ylabel(r'Moment (emu/$cm^3$)')

    # 処理後mu_B/Mnプロット
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(data['Temperature (K)'],
             data['Moment of Ferromagnet (mu_B/Mn)'])
    x, y = tangent_line(data['Temperature (K)'][peak_ind],
                        data['Moment of Ferromagnet (mu_B/Mn)'][peak_ind], dMdT[peak_ind])
    ax4.plot(x, y)
    ax4.set_xlabel('Temperature (K)')
    ax4.set_ylabel(r'Moment ($\mu_B$/Mn)')

    # データ保存
    data.to_csv('analyzed/X918_LSMO-SiO2-Si_axis100_MT_5-400K_400Oe.csv')

    # 描画
    plt.show()


main()
