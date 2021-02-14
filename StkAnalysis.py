# coding=utf-8
import pandas as pd
from matplotlib import ticker
from pandas.plotting import register_matplotlib_converters
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import ticker
# from mpl_toolkits.mplot3d import Axes3D
import csv
import math
from os import listdir
import talib
from talib import abstract
from mplfinance.original_flavor import candlestick_ohlc
import numpy as np
from datetime import timedelta, datetime
from scipy.stats import shapiro, ttest_1samp, kstest, norm

code_lt, name_lt = [], []
with open('D:/stocks/filter.txt', newline='\n', encoding='utf-8') as filter:
    rd = list(csv.reader(filter))
    for row in rd:
        code_lt.append(row[0])
        name_lt.append(row[1])
matype_dict = {'SMA': 0, 'EMA': 1, 'WMA': 2, 'DEMA': 3,
               'TEMA': 4, 'TRIMA': 5, 'KAMA': 6, 'MAMA': 7, 'T3': 8}
reverse_dict = {v: k for k, v in matype_dict.items()}


def KDCross(code, mode, fk, sk, sd, ma_type):
    filename = '-'.join((str(fk), str(sk), str(sd))) + mode + code + '.csv'
    print(mode, filename)
    if code in code_lt:
        mode_dict = {'m': 'D:/2016_2019/monp/m',
                     'w': 'D:/2016_2019/weekp/w', 'p': 'D:/2016_2019/p/p'}
        df = pd.read_csv(mode_dict[mode] + code + '.csv', parse_dates=['date'])
        KD_dict = {'ind': [], 'date': [], 'preslowk': [], 'slowk': [],
                   'preslowd': [], 'slowd': [], 'closechg1': [], 'closechg2': [], 'closechg3': [], 'closechg4': [],
                   'closechg5': [], 'closechg6': [], 'closechg7': [], 'closechg8': [],
                   'closechg9': [], 'closechg10': [], 'closechg20': [], 'k3': [], 'k5': [], 'k10': [],
                   'd3': [], 'd5': [], 'd10': [], 'crossover': [], 'both_chg': []}
        slowk, slowd = talib.STOCH(df['high'], df['low'], df['close'], fastk_period=fk, slowk_period=sk,
                                   slowk_matype=ma_type, slowd_period=sd, slowd_matype=ma_type)
        key_tup = tuple(KD_dict.keys())
        df['slowk'] = slowk
        df['slowd'] = slowd
        for k in range(len(df)):
            if df.loc[k, 'slowk'] < 0 or df.loc[k, 'slowd'] < 0:
                with open('D:/2016_2019/KDerror.txt', 'a', newline='\n', encoding='utf-8') as kdf:
                    wr = csv.writer(kdf)
                    wr.writerow([mode, filename, 'index:' + str(k)])
        input_lt = [(-1, 'slowk'), (0, 'slowk'),
                    (-1, 'slowd'), (0, 'slowd')]
        for j in range(1, 11):
            input_lt.append((j, 'close'))
        input_lt = input_lt + [(20, 'close'), (3, 'slowk'), (5, 'slowk'),
                               (10, 'slowk'), (3, 'slowd'), (5, 'slowd'), (10, 'slowd')]
        for i in range(1, len(df)):
            tdy_k, tdy_d, prek, pred = df.loc[i, 'slowk'], df.loc[i,
                                                                  'slowd'], df.loc[i - 1, 'slowk'], df.loc[i - 1, 'slowd']
            if tdy_k > tdy_d and prek <= pred:
                KD_dict['ind'].append(i)
                KD_dict['date'].append(df.loc[i, 'date'])
                for e, ele in enumerate(input_lt, start=2):
                    if i + ele[0] < len(df):
                        if e > 5 and ele[1] == 'close':
                            KD_dict[key_tup[e]].append(
                                math.log(df.loc[i + ele[0], ele[1]] / df.loc[i, ele[1]]))
                        else:
                            KD_dict[key_tup[e]].append(
                                df.loc[i + ele[0], ele[1]])
                    else:
                        KD_dict[key_tup[e]].append(np.NaN)
                KD_dict['crossover'].append(True)
                if tdy_k > prek and tdy_d > pred:
                    KD_dict['both_chg'].append(True)
                else:
                    KD_dict['both_chg'].append(False)
            elif tdy_k < tdy_d and prek >= pred:
                KD_dict['ind'].append(i)
                KD_dict['date'].append(df.loc[i, 'date'])
                for e, ele in enumerate(input_lt, start=2):
                    if i + ele[0] < len(df):
                        if e > 5 and ele[1] == 'close':
                            KD_dict[key_tup[e]].append(
                                math.log(df.loc[i + ele[0], ele[1]] / df.loc[i, ele[1]]))
                        else:
                            KD_dict[key_tup[e]].append(
                                df.loc[i + ele[0], ele[1]])
                    else:
                        KD_dict[key_tup[e]].append(np.NaN)
                KD_dict['crossover'].append(False)
                if tdy_k < prek and tdy_d < pred:
                    KD_dict['both_chg'].append(True)
                else:
                    KD_dict['both_chg'].append(False)
        if KD_dict['ind'] != []:
            pd.DataFrame(KD_dict).to_csv(
                'D:/2016_2019/analysis/KDCross/' + filename, index=False)
            print('Done', filename)


# chk: [1, 0, 0] plot: [['MACD', 'DMI', '0.66', '0.03'], ['無', '無', 21, 55], ['EMA', 'EMA', 'EMA', 'EMA'], [21, 'EMA', 2.0, 2.2, 3.0]]
# StkPlot('0000', 0, [1, 0, 0], [['MACD', 'DMI', '0.66', '0.03'], ['無', '無', 21, 55], ['EMA', 'EMA', 'EMA', 'EMA'], [21, 'EMA', 2.0, 2.2, 3.0]], mode)
def CheckNorm(file_lt):
    new_dict = {'file': [], 'len': [], 'mean': [], 'median': [], 'stderr': [],
                'stat': [], 'pval': []}

    for filename in file_lt:
        df = pd.read_csv(filename, parse_dates=['date'])
        test_data = np.log(df['close']).diff(1)
        test_data.dropna(inplace=True)
        if len(test_data) > 35:
            loc, scale = norm.fit(test_data.values)
            """
            if len(test_data) < 5000:
                print('length:', len(test_data), filename)
                shapiro_res = shapiro(test_data)
                stat, pval = shapiro_res.statistic, shapiro_res.pvalue
            else:
            """
            n = norm(loc=loc, scale=scale)
            ks_res = kstest(test_data, n.cdf)
            stat, pval = ks_res[0], ks_res[1]
            new_dict['file'].append(filename[-9:-4])
            new_dict['len'].append(len(test_data))
            new_dict['mean'].append(loc)
            new_dict['median'].append(float(np.median(test_data)))
            new_dict['stderr'].append(scale)
            new_dict['stat'].append(stat)
            new_dict['pval'].append(pval)
        else:
            print('Length:', len(test_data))
    pd.DataFrame(new_dict).to_csv(
        'D:/2016_2019/analysis/NormDist(all ks).csv', index=False)


def OneSampleTTest(df, popmean):
    print('Length of data:', len(df))
    ttest_res = ttest_1samp(df, popmean)
    t_stat, t_pval = ttest_res.statistic, ttest_res.pvalue
    if t_pval < 0.05:
        print('有顯著差異', t_stat, t_pval)
    else:
        print('無顯著差異', t_stat, t_pval)
    return {'stat': t_stat, 'pvalue': t_pval}


def KDLevel(file):
    df = pd.read_csv('D:/2016_2019/analysis/KDCross/' +
                     file, parse_dates=['date'])
    df['preklevel'] = pd.cut(df['preslowk'], [0, 50, 100], include_lowest=True,
                             labels=[0, 50])
    df['klevel'] = pd.cut(df['slowk'], [0, 50, 100], include_lowest=True,
                          labels=[0, 50])
    df['predlevel'] = pd.cut(df['preslowd'], [0, 50, 100], include_lowest=True,
                             labels=[0, 50])
    df['dlevel'] = pd.cut(df['slowd'], [0, 50, 100], include_lowest=True,
                          labels=[0, 50])
    df.to_csv('D:/2016_2019/analysis/KDCross/' +
              file, index=False)


def KDPlot(file, col, crossover, closechg):
    plt.close('all')
    plt.rcParams["figure.figsize"] = (10, 8)
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('ggplot')
    mavcolors = ['#00BFFF', '#FF0088', '#00ad90']
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    df = pd.read_csv('D:/2016_2019/analysis/KDCross/' +
                     file, parse_dates=['date'])
    mode_dict = {'m': 'monp', 'w': 'weekp', 'p': 'p'}
    pr_df = pd.read_csv('D:/2016_2019/' + mode_dict[file[-9]] +
                        '/' + file[-9:], parse_dates=['date'])
    ys = (0, 50)
    label_dict = {0: ' < 50', 50: ' ≧ 50'}
    dt_str = list(set(pr_df['date'].dt.strftime('%Y').values))
    dt_str.sort()
    if '2021' in dt_str:
        dt_str.remove('2021')
    dt_str = pd.Series(dt_str, dtype=str)
    for num, val in enumerate(ys):
        zs = []
        for pos, year in enumerate(dt_str):
            cond01 = df['date'].dt.strftime('%Y') == year
            cond02 = df[col] == val
            cond03 = df['crossover'] == crossover
            data = df[cond01 & cond02 & cond03][closechg]
            new = data.dropna()
            data_len = len(new)
            med_val = np.median(100 * new)
            if not pd.isnull(med_val):
                zs.append(med_val)
            else:
                print(year, val)
                med_val = 0
                zs.append(0)
            # """
            ax.text(pos, val, med_val, str(data_len),
                    fontdict={'fontsize': 'xx-small'})
            # """
        zs = pd.Series(zs, dtype=float)
        ax.bar(dt_str, zs, zs=val, zdir='y',
               color=mavcolors[num], alpha=0.7, label=col + label_dict[val])
        ax.legend(framealpha=0, markerscale=0.6, fontsize='x-small')
    ax.set_xlabel('年', fontdict={'fontsize': 'small'})
    ax.set_ylabel(col, fontdict={'fontsize': 'small'})
    ax.set_zlabel(closechg + '(%)', fontdict={'fontsize': 'small'})
    ax.tick_params(axis='x', labelsize='x-small')
    # ax.tick_params(axis='y', labelsize='small')
    ax.xaxis.set_major_locator(
        locator=ticker.MultipleLocator(len(dt_str) // 7))
    subtitle = '黃金' if crossover else '死亡'
    ax.set_title(name_lt[code_lt.index(file[-8:-4])] +
                 ':KD' + subtitle + '交叉')
    plt.show()


def ClosechgPlot(file, crossover, closechg_lt):
    font = 7
    plt.close('all')
    plt.rcParams["figure.figsize"] = (10, 8)
    plt.rcParams['axes.titlesize'] = font
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('ggplot')
    mavcolors = ['#00BFFF', '#fa0c54', '#007f8b',
                 '#d9910b', '#0bb3b0',
                 '#4B0082', '#FF8C00', '#16d9f2', '#d9d616', '#d91698']
    fig = plt.figure(dpi=150)
    ax = fig.gca(projection='3d')
    df = pd.read_csv('D:/2016_2019/analysis/KDCross/' +
                     file, parse_dates=['date'])
    mode_dict = {'m': 'monp', 'w': 'weekp', 'p': 'p'}
    label_dict = {'m': '月', 'w': '周', 'p': '日'}
    pr_df = pd.read_csv('D:/2016_2019/' + mode_dict[file[-9]] +
                        '/' + file[-9:], parse_dates=['date'])
    dt_str = list(set(pr_df['date'].dt.strftime('%Y').values))
    dt_str.sort()
    if '2021' in dt_str:
        dt_str.remove('2021')
    int_dt_str = [int(ele) for ele in dt_str]
    #dt_str = pd.Series(dt_str, dtype=str)
    pr_lt = []
    for y in dt_str:
        cond02 = pr_df['date'].dt.strftime('%Y') == y
        highest = max(pr_df[cond02]['high'])
        pr_lt.append(highest)
    pr_lt = pd.Series(pr_lt, dtype=float)
    for num, val in enumerate(closechg_lt):
        ys = []
        for pos, year in enumerate(dt_str):
            cond01 = df['date'].dt.strftime('%Y') == year
            cond03 = df['crossover'] == crossover
            data = df[cond01 & cond03]['closechg' + str(val)]
            new = data.dropna()
            data_len = len(new)
            med_val = np.median(100 * new)
            if not pd.isnull(med_val):
                ys.append(med_val)
            else:
                print(year, val)
                med_val = 0
                ys.append(0)
            """
            ax.text(pos, val, med_val, str(data_len),
                    fontdict={'fontsize': 'xx-small'})
            """
        ys = pd.Series(ys, dtype=float)
        ax.bar(int_dt_str, ys, zs=val, zdir='y', alpha=0.7, color=mavcolors[num],
               label=str(closechg_lt[num]))
        ax.legend(framealpha=0, markerscale=0.3, fontsize=font)
    ax.set_xlabel('年', fontdict={'fontsize': font})
    ax.set_ylabel('交叉後' + label_dict[file[-9]] +
                  '數', fontdict={'fontsize': font})
    ax.set_zlabel('漲跌幅(%)', fontdict={'fontsize': font})
    ax.tick_params(axis='x', labelsize=font)
    ax.set_yticks(closechg_lt)
    ax.tick_params(axis='y', labelsize=font)
    ax.tick_params(axis='z', labelsize=font)
    ax.xaxis.set_major_locator(
        locator=ticker.MultipleLocator(len(dt_str) // 6))
    subtitle = '黃金' if crossover else '死亡'
    ax.set_title('KD' + subtitle + '交叉後漲跌幅' + '（' +
                 name_lt[code_lt.index(file[-8:-4])] + '）')
    plt.show()


col = 'klevel'
mode = 'y'
closechg = 'closechg20'
kd_lt = listdir(r"D:\2016_2019\analysis\KDCross")
f = '14-3-3p1000.csv'
# KDPlot(f, col, False, closechg)
#day_lt = np.arange(1, 4, dtype=int)
#ClosechgPlot(f, True, day_lt)
