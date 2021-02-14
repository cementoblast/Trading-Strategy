import numpy as np
import pandas as pd
import talib
from talib import abstract
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib import ticker, patches
import matplotlib.lines as mlines
from pandas.plotting import register_matplotlib_converters
import csv
dfname = (r"D:\2016_2019\analysis\HMA\hma9b.csv",
          r"D:\2016_2019\analysis\HMA\hma16b.csv")
code_dict = {}
with open('D:/stocks/filter.txt', newline='\n', encoding='utf-8') as filter:
    for row in csv.reader(filter):
        code_dict[row[0]] = row[1]


def ShowAnnotationWithHMA(code, file, chk_lt, plot_lt, a, b):
    df = pd.read_csv('D:/2016_2019/weekp/w' + code +
                     '.csv', parse_dates=['date'])
    trade_lt = []
    data_lt = []
    time_lt = []

    def plot_indicator(axname, indicator):
        if indicator == 'MACD':
            macd9 = abstract.MACDEXT(df, fastperiod=12, fastmatype=1,
                                     slowperiod=26, slowmatype=1,
                                     signalperiod=9, signalmatype=1)
            df['macdhist'] = macd9['macdhist']
            red_bar = np.where(df[start_idx:last_idx + 1]['macdhist'] > 0,
                               df[start_idx:last_idx + 1]['macdhist'], 0)
            green_bar = np.where(df[start_idx:last_idx + 1]['macdhist'] < 0,
                                 df[start_idx:last_idx + 1]['macdhist'], 0)
            axname.bar(time_lt, red_bar, label='Red bar',
                       color='#e01055', width=0.6, linewidth=0)
            axname.bar(time_lt, green_bar, label='Green bar',
                       color='#008c64', width=0.6, linewidth=0)
            axname.tick_params(axis='y', labelsize='x-small')
        elif indicator == 'NATR':
            df['natr5'] = abstract.NATR(df, timeperiod=5)
            df['natr21'] = abstract.NATR(df, timeperiod=21)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['natr5'], label='5 NATR', color='#ff9d26',
                        linewidth=0.8)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['natr21'], label='21 NATR', color='#13d1f2',
                        linewidth=0.8)
            axname.legend(framealpha=0, fontsize='x-small', markerscale=0.8)
            axname.tick_params(axis='y', labelsize='x-small')
        elif indicator == 'DMI':
            df['ADXR'] = abstract.ADXR(df, timeperiod=14)
            df['DI+'] = abstract.PLUS_DI(df, timeperiod=14)
            df['DI-'] = abstract.MINUS_DI(df, timeperiod=14)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['ADXR'],
                        label='ADXR', color='#ff6a00', linewidth=0.8)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['DI+'],
                        label='DI+', color='#f21164', linewidth=0.8)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['DI-'],
                        label='DI-', color='#008B8B', linewidth=0.8)  # 008c77
            axname.legend(framealpha=0, fontsize='x-small', markerscale=0.8)
            axname.tick_params(axis='y', labelsize='x-small')
        else:
            print('Indicator not found')
    if file != 0:
        # "D:\2016_2019\rawbacktest\b0405-2010111125.csv"
        rec = pd.read_csv(file, parse_dates=['buy_date', 'sell_date'])
        for i in range(len(rec)):
            if rec.loc[i, 'code'] == int(code):
                if file[-5] == 'b':
                    trade_lt.append(
                        (rec.loc[i, 'buy_date'], rec.loc[i, 'buy_p'], rec.loc[i, 'sell_date'], rec.loc[i, 'sell_p']))
                else:
                    trade_lt.append(
                        (rec.loc[i, 'sell_date'], rec.loc[i, 'sell_p'], rec.loc[i, 'buy_date'], rec.loc[i, 'buy_p']))
        if len(trade_lt) != 0:
            trade_lt.sort(key=lambda x: x[0])
            sort_last_lt = sorted(trade_lt, key=lambda x: x[2])
            fst_date = trade_lt[0][0]
            last_date = sort_last_lt[-1][2]
            fst_date_idx = df[df['date'] == fst_date].index.to_list()[0]
            last_date_idx = df[df['date'] == last_date].index.to_list()[0]
            if fst_date_idx > 50:
                start_idx = fst_date_idx - 50
            else:
                start_idx = 0
            if last_date_idx + 50 < len(df) - 1:
                last_idx = last_date_idx + 50
            else:
                last_idx = len(df) - 1
            for e, idx in enumerate(range(start_idx, last_idx + 1)):
                # t = date2num(df.loc[idx, 'date'])
                t = df.loc[idx, 'date'].strftime('%Y-%m-%d')
                time_lt.append(t)
                data_lt.append(
                    (e, df.loc[idx, 'open'], df.loc[idx, 'high'], df.loc[idx, 'low'], df.loc[idx, 'close']))
        else:
            print('No record.')
            return 1
    else:
        start_idx, last_idx = 0, len(df) - 1
        for e, idx in enumerate(range(len(df))):
            t = df.loc[idx, 'date'].strftime('%Y-%m-%d')
            time_lt.append(t)
            data_lt.append(
                (e, df.loc[idx, 'open'], df.loc[idx, 'high'], df.loc[idx, 'low'], df.loc[idx, 'close']))
    plt.close('all')
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('ggplot')
    mavcolors = ['#00BFFF', '#ffd000', '#FF0088', '#00ad90',
                 '#4B0082', '#FF8C00', '#0bb3b0', '#11edab']

    def format_date(x, pos=None):
        if x < 0 or x > len(time_lt) - 1:
            return ''
        return time_lt[int(x)]
    fig = plt.figure(figsize=(24, 15))
    axk_color = '#d1e2e3'
    axv_color = '#d2e2e3'
    matype_dict = {'SMA': 0, 'EMA': 1, 'WMA': 2, 'DEMA': 3,
                   'TEMA': 4, 'TRIMA': 5, 'KAMA': 6, 'MAMA': 7, 'T3': 8}
    if chk_lt[0] == 0:
        k_fraction, sub_fraction, blank, left_space, right_space, bottom_space, top_space = 0.7, 0.3, 0.01, 0.07, 0.02, 0.05, 0.05
        axk = fig.add_axes([left_space, 1 - k_fraction + blank, 1 -
                            left_space - right_space, k_fraction - blank - top_space])
        axv = fig.add_axes([left_space, bottom_space, 1 - left_space -
                            right_space, sub_fraction - bottom_space], sharex=axk)
    else:
        k_fraction, bottom_space, vol_fraction, blank, left_space, right_space, top_space = 0.5, 0.05, 0.2, 0.01, 0.07, 0.05, 0.05
        sub_fraction = (1 - bottom_space - k_fraction -
                        vol_fraction - blank * 3) / 2
        axk = fig.add_axes([left_space, 1 - k_fraction, 1 -
                            left_space - right_space, k_fraction - top_space])
        axv = fig.add_axes([left_space, bottom_space, 1 -
                            left_space - right_space, vol_fraction], sharex=axk)
        ax0 = fig.add_axes([left_space, bottom_space + vol_fraction +
                            blank, 1 - left_space - right_space, sub_fraction], sharex=axk)
        ax1 = fig.add_axes([left_space, bottom_space + vol_fraction + sub_fraction +
                            2 * blank, 1 - left_space - right_space, sub_fraction], sharex=axk)
        plt.setp(ax0.get_xticklabels(), visible=False)
        plt.setp(ax1.get_xticklabels(), visible=False)
        ax0.set_ylabel(ylabel=plot_lt[0][0], fontdict={'fontsize': 'x-small'})
        ax1.set_ylabel(ylabel=plot_lt[0][1], fontdict={'fontsize': 'x-small'})
        ax0.set_facecolor(axk_color)
        ax1.set_facecolor(axv_color)
        plot_indicator(ax0, plot_lt[0][0])
        plot_indicator(ax1, plot_lt[0][1])
    axk.set_facecolor(axk_color)
    axv.set_facecolor(axv_color)
    plt.setp(axk.get_xticklabels(), visible=False)
    plt.setp(axv.get_xticklabels(), visible=True)
    axk.set_ylabel(ylabel='Price', fontdict={'fontsize': 'small'})
    axv.set_ylabel(ylabel='Vol', fontdict={'fontsize': 'small'})
    axv.tick_params(axis='x', labelsize='small')
    axv.tick_params(axis='y', labelsize='small')
    axk.tick_params(axis='y', labelsize='small')
    axv.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    axk.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    axv.xaxis.set_major_locator(
        locator=ticker.MultipleLocator(len(time_lt) // 7))
    axk.xaxis.set_major_locator(
        locator=ticker.MultipleLocator(len(time_lt) // 7))
    candlestick_ohlc(axk, data_lt, width=0.6, colorup='#e01055',
                     colordown='#008c64', alpha=1)
    df['closechg'] = df['close'].diff()
    df['closechg'].fillna(0, inplace=True)
    df['red vol'] = np.where(df['closechg'] > 0, df['vol'], 0)
    df['orange vol'] = np.where(df['closechg'] == 0, df['vol'], 0)
    df['green vol'] = np.where(df['closechg'] < 0, df['vol'], 0)

    axv.bar(time_lt, df[start_idx:last_idx + 1]['red vol'], width=0.6,
            linewidth=0, color='#d10026', alpha=1, label='vol')
    axv.bar(time_lt, df[start_idx:last_idx + 1]['orange vol'], width=0.6,
            linewidth=0, color='#e09900', alpha=1, label='vol')
    axv.bar(time_lt, df[start_idx:last_idx + 1]['green vol'], width=0.6,
            linewidth=0, color='#009940', alpha=1, label='vol')

    if chk_lt[1] == 1:
        df['mama'], df['fama'] = talib.MAMA(
            df['close'], fastlimit=plot_lt[0][2], slowlimit=plot_lt[0][3])
        axk.plot(time_lt, df[start_idx:last_idx + 1]['mama'],
                 label='MAMA', color=mavcolors[-2], linewidth=0.7)
        axk.plot(time_lt, df[start_idx:last_idx + 1]['fama'],
                 label='FAMA', color=mavcolors[-1], linewidth=0.7)
        axk.fill_between(time_lt, df[start_idx:last_idx + 1]['mama'], df[start_idx:last_idx + 1]['fama'],
                         where=df[start_idx:last_idx + 1]['mama'] > df[start_idx:last_idx + 1]['fama'], color='#FF44AA',
                         alpha=0.5)  # 多
        axk.fill_between(time_lt, df[start_idx:last_idx + 1]['mama'], df[start_idx:last_idx + 1]['fama'],
                         where=df[start_idx:last_idx + 1]['mama'] < df[start_idx:last_idx + 1]['fama'], color='#0b7356',
                         alpha=0.5)  # 空
    if chk_lt[2] == 1:
        df['ht'] = talib.HT_TRENDLINE(df['close'])
        axk.plot(time_lt, df[start_idx:last_idx + 1]['ht'],
                 label='HT trendline', color='#fa8b02', linewidth=0.7)  # fa8b02
        axk.fill_between(time_lt, df[start_idx:last_idx + 1]['ht'], df[start_idx:last_idx + 1]['close'],
                         where=df[start_idx:last_idx +
                                  1]['close'] > df[start_idx:last_idx + 1]['ht'],
                         color='#0cb5f2',
                         alpha=0.5)  # 多
        axk.fill_between(time_lt, df[start_idx:last_idx + 1]['ht'], df[start_idx:last_idx + 1]['close'],
                         where=df[start_idx:last_idx +
                                  1]['close'] < df[start_idx:last_idx + 1]['ht'],
                         color='#ffea00',
                         alpha=0.5)  # 空
    if type(a) == type(b) == int and a != b:
        n_tup = (a, b)
        hma_colors = (('#e30048', '#00d423'),
                      ('#e08402', '#00ccc9'))
        for hma_i, n in enumerate(n_tup):
            half_n = int(round(n / 2, 0))
            root_n = int(round(pow(n, 0.5), 0))
            c_copy = pd.DataFrame({'close': []})
            hma_1 = 2 * abstract.WMA(df, half_n)
            hma_2 = abstract.WMA(df, n)
            c_copy['close'] = hma_1 - hma_2
            col = 'hma' + str(n)
            df[col] = abstract.WMA(c_copy, root_n)
            df[col + 'd'] = df[col].diff()
            df['up-' + col] = np.where(df[col + 'd'] > 0, df[col], np.NaN)
            df['down-' + col] = np.where(df[col + 'd']
                                         <= 0, df[col], np.NaN)
            axk.scatter(time_lt, df[start_idx:last_idx + 1]['up-' + col], label=col + '(上升)',
                        color=hma_colors[hma_i][0], s=2)
            axk.scatter(time_lt, df[start_idx:last_idx + 1]['down-' + col], label=col + '(下降)', color=hma_colors[hma_i][1],
                        s=2)
    else:
        print('Argument error:', a, b)
        return 'err'
    all_ma_lt, k1 = [], 0
    for num, ma_day in enumerate(plot_lt[1]):
        ma_type = plot_lt[2][num]
        if type(ma_day) == int and ma_type != '無' and (ma_day, ma_type) not in all_ma_lt:
            all_ma_lt.append((ma_day, ma_type))
            ma_label = str(ma_day) + ma_type
            df[ma_label] = abstract.MA(
                df, timeperiod=ma_day, matype=matype_dict[ma_type])
            axk.plot(time_lt, df[start_idx:last_idx + 1][ma_label], label=ma_label, color=mavcolors[k1],
                     linewidth=0.6)
            k1 += 1
    if type(plot_lt[3][0]) == int and plot_lt[3][1] != '無' and (plot_lt[3][2] != '無' or plot_lt[3][3] != '無' or plot_lt[3][4] != '無'):
        bb_color = ['#FF1493', '#FF69B4', '#FFB6C1']
        for e, dev in enumerate(plot_lt[3][2:]):
            if dev != '無' and dev != '':
                upperband, middleband, lowerband = talib.BBANDS(df['close'],
                                                                timeperiod=plot_lt[3][0], nbdevup=dev, nbdevdn=dev,
                                                                matype=matype_dict[plot_lt[3][1]])
                if e == 0 and (all_ma_lt == [] or (plot_lt[3][0], plot_lt[3][1]) not in all_ma_lt):
                    df['midband'] = middleband
                    axk.plot(time_lt, df[start_idx:last_idx + 1]['midband'], color=bb_color[e],
                             linewidth=0.5, linestyle='dashed', label='布林中軌({:n}{})'.format(plot_lt[3][0], '日'))
                df['upband' + str(dev)] = upperband
                df['lowband' + str(dev)] = lowerband
                axk.plot(time_lt, df[start_idx:last_idx + 1]['upband' + str(dev)], color=bb_color[e], linewidth=0.5,
                         linestyle='dashed', label='{}倍標準差'.format(str(dev)))
                axk.plot(time_lt, df[start_idx:last_idx + 1]['lowband' + str(dev)], color=bb_color[e], linewidth=0.5,
                         linestyle='dashed')
    axk.legend(framealpha=0, markerscale=0.8, fontsize='x-small')
    name = code_dict[code] if code in code_dict else code
    axk.set_title(label=name + '（' + str(code) + '）',
                  fontdict={'fontsize': 'small'})
    if file != 0:
        if file[-5] == 'b':
            for num, trade in enumerate(trade_lt, start=1):
                low_idx, high_idx = df[df['date'] == trade[0]
                                       ].index, df[df['date'] == trade[2]].index
                low, high = df.loc[low_idx, 'low'], df.loc[high_idx, 'high']
                buy_date = trade[0].strftime('%Y-%m-%d')
                sell_date = trade[2].strftime('%Y-%m-%d')
                cp_ratio = round(100 * (trade[3] / trade[1] - 1), 1)
                color_tup = ('#b31522', '#e60b1d') if cp_ratio > 0 else (
                    '#02a876', '#2cdba7')
                axk.annotate(text='b' + str(num), xy=(buy_date, low * 0.99), xytext=(0, -15),
                             textcoords='offset points', arrowprops={'arrowstyle': '->', 'facecolor': color_tup[1], 'edgecolor': color_tup[1]},
                             annotation_clip=False, color=color_tup[0])
                axk.annotate(text='s' + str(num) + ':' + str(cp_ratio) + '%', xy=(sell_date, high * 1.01), xytext=(0, 10),
                             textcoords='offset points', arrowprops={'arrowstyle': '->', 'facecolor': color_tup[1], 'edgecolor': color_tup[1]},
                             annotation_clip=False, color=color_tup[0])
        else:
            for num, trade in enumerate(trade_lt, start=1):
                low_idx, high_idx = df[df['date'] == trade[2]
                                       ].index, df[df['date'] == trade[0]].index
                low, high = df.loc[low_idx, 'low'], df.loc[high_idx, 'high']
                sell_date = trade[0].strftime('%Y-%m-%d')
                buy_date = trade[2].strftime('%Y-%m-%d')
                cp_ratio = round(100 * (trade[1] / trade[3] - 1), 1)
                color_tup = ('#b31522', '#e60b1d') if cp_ratio > 0 else (
                    '#02a876', '#2cdba7')
                axk.annotate('s' + str(num), xy=(sell_date, high * 1.01), xytext=(0, 10),
                             textcoords='offset points', arrowprops={'arrowstyle': '->', 'facecolor': color_tup[1], 'edgecolor': color_tup[1]}, annotation_clip=False, color=color_tup[0])
                axk.annotate('b' + str(num) + ':' + str(cp_ratio) + '%', xy=(buy_date, low * 0.99), xytext=(0, -15),
                             textcoords='offset points', arrowprops={'arrowstyle': '->', 'facecolor': color_tup[1], 'edgecolor': color_tup[1]}, annotation_clip=False, color=color_tup[0])
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()
    return 0


def ExtraPlot(code, file, chk_lt, plot_lt, a, b, mode):
    mode_dict = {'p': 'D:/2016_2019/p/p', 'w': 'D:/2016_2019/weekp/w'}
    df = pd.read_csv(mode_dict[mode] + code +
                     '.csv', parse_dates=['date'])
    trade_lt = []
    data_lt = []
    time_lt = []

    def plot_indicator(axname, indicator):
        if indicator == 'MACD':
            macd9 = abstract.MACDEXT(df, fastperiod=12, fastmatype=1,
                                     slowperiod=26, slowmatype=1,
                                     signalperiod=9, signalmatype=1)
            df['macdhist'] = macd9['macdhist']
            red_bar = np.where(df[start_idx:last_idx + 1]['macdhist'] > 0,
                               df[start_idx:last_idx + 1]['macdhist'], 0)
            green_bar = np.where(df[start_idx:last_idx + 1]['macdhist'] < 0,
                                 df[start_idx:last_idx + 1]['macdhist'], 0)
            axname.bar(time_lt, red_bar, label='Red bar',
                       color='#e01055', width=0.6, linewidth=0)
            axname.bar(time_lt, green_bar, label='Green bar',
                       color='#008c64', width=0.6, linewidth=0)
            axname.tick_params(axis='y', labelsize='x-small')
        elif indicator == 'NATR':
            tr = pd.DataFrame({'h-l': []})
            tr['h-l'] = df['high'] / df['low'] - 1
            df['shift_close'] = df['close'].shift(1)
            tr['h-pc'] = df['high'] / df['shift_close'] - 1
            tr['l-pc'] = df['low'] / df['shift_close'] - 1
            tr['h-pc'] = tr['h-pc'].abs()
            tr['l-pc'] = tr['l-pc'].abs()

            tr['close'] = tr.max(axis=1) * 100
            df['TR'] = abstract.WMA(tr, timeperiod=5)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['TR'],
                        label='True Range', color='#0088bb', linewidth=0.7)  # 008c77
            """
            axname.plot(time_lt, df[start_idx:last_idx + 1]['bias5'],
                        label='BIAS5', color='#e07f00', linewidth=0.7)  # 008c77
            df['natr5'] = abstract.NATR(df, timeperiod=5)
            df['natr21'] = abstract.NATR(df, timeperiod=21)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['natr5'], label='5 NATR', color='#ff9d26',
                        linewidth=0.8)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['natr21'], label='21 NATR', color='#13d1f2',
                        linewidth=0.8)
            """
            axname.legend(framealpha=0, fontsize='x-small', markerscale=0.8)
            axname.tick_params(axis='y', labelsize='x-small')
        elif indicator == 'DMI':
            df['ema233'] = abstract.EMA(df, timeperiod=233)
            df['ema89'] = abstract.EMA(df, timeperiod=89)
            df['ema55'] = abstract.EMA(df, timeperiod=55)
            df['ema21'] = abstract.EMA(df, timeperiod=21)
            df['ema13'] = abstract.EMA(df, timeperiod=13)
            df['ema5'] = abstract.EMA(df, timeperiod=5)
            df['div1'] = df[['ema5', 'ema21', 'ema55',
                             'high', 'low', 'close']].sem(axis=1)
            df['div2'] = df[['ema5', 'ema21', 'ema55',
                             'close']].sem(axis=1)

            df['DI+'] = abstract.PLUS_DI(df, timeperiod=14)
            df['DI-'] = abstract.MINUS_DI(df, timeperiod=14)
            df['DI-xDIV1'] = df['DI-'] * df['div1']
            df['DI-xDIV2'] = df['DI-'] * df['div2']
            axname.plot(time_lt, df[start_idx:last_idx + 1]['DI-xDIV1'],
                        label='DI+xDIV1', color='#ff0044', linewidth=0.7)
            axname.plot(time_lt, df[start_idx:last_idx + 1]['DI-xDIV2'],
                        label='DI-xDIV2', color='#008a43', linewidth=0.7)
            axname.legend(framealpha=0, fontsize='x-small', markerscale=0.8)
            axname.tick_params(axis='y', labelsize='x-small')
        else:
            print('Indicator not found')
    if file != 0:
        # "D:\2016_2019\rawbacktest\b0405-2010111125.csv"
        rec = pd.read_csv(file, parse_dates=['buy_date', 'sell_date'])
        for i in range(len(rec)):
            if rec.loc[i, 'code'] == int(code):
                if file[-5] == 'b':
                    trade_lt.append(
                        (rec.loc[i, 'buy_date'], rec.loc[i, 'buy_p'], rec.loc[i, 'sell_date'], rec.loc[i, 'sell_p']))
                else:
                    trade_lt.append(
                        (rec.loc[i, 'sell_date'], rec.loc[i, 'sell_p'], rec.loc[i, 'buy_date'], rec.loc[i, 'buy_p']))
        if len(trade_lt) != 0:
            trade_lt.sort(key=lambda x: x[0])
            sort_last_lt = sorted(trade_lt, key=lambda x: x[2])
            fst_date = trade_lt[0][0]
            last_date = sort_last_lt[-1][2]
            fst_date_idx = df[df['date'] == fst_date].index.to_list()[0]
            last_date_idx = df[df['date'] == last_date].index.to_list()[0]
            if fst_date_idx > 50:
                start_idx = fst_date_idx - 50
            else:
                start_idx = 0
            if last_date_idx + 50 < len(df) - 1:
                last_idx = last_date_idx + 50
            else:
                last_idx = len(df) - 1
            for e, idx in enumerate(range(start_idx, last_idx + 1)):
                # t = date2num(df.loc[idx, 'date'])
                t = df.loc[idx, 'date'].strftime('%Y-%m-%d')
                time_lt.append(t)
                data_lt.append(
                    (e, df.loc[idx, 'open'], df.loc[idx, 'high'], df.loc[idx, 'low'], df.loc[idx, 'close']))
        else:
            print('No record.')
            return 1
    else:
        start_idx, last_idx = 0, len(df) - 1
        for e, idx in enumerate(range(len(df))):
            t = df.loc[idx, 'date'].strftime('%Y-%m-%d')
            time_lt.append(t)
            data_lt.append(
                (e, df.loc[idx, 'open'], df.loc[idx, 'high'], df.loc[idx, 'low'], df.loc[idx, 'close']))
    plt.close('all')
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('ggplot')
    mavcolors = ['#00BFFF', '#ffd000', '#FF0088', '#00ad90',
                 '#4B0082', '#FF8C00', '#0bb3b0', '#11edab']

    def format_date(x, pos=None):
        if x < 0 or x > len(time_lt) - 1:
            return ''
        return time_lt[int(x)]
    fig = plt.figure(figsize=(24, 15))
    axk_color = '#d1e2e3'
    axv_color = '#d2e2e3'
    matype_dict = {'SMA': 0, 'EMA': 1, 'WMA': 2, 'DEMA': 3,
                   'TEMA': 4, 'TRIMA': 5, 'KAMA': 6, 'MAMA': 7, 'T3': 8}
    if chk_lt[0] == 0:
        k_fraction, sub_fraction, blank, left_space, right_space, bottom_space, top_space = 0.7, 0.3, 0.01, 0.07, 0.02, 0.05, 0.05
        axk = fig.add_axes([left_space, 1 - k_fraction + blank, 1 -
                            left_space - right_space, k_fraction - blank - top_space])
        axv = fig.add_axes([left_space, bottom_space, 1 - left_space -
                            right_space, sub_fraction - bottom_space], sharex=axk)
    else:
        k_fraction, bottom_space, vol_fraction, blank, left_space, right_space, top_space = 0.5, 0.05, 0.2, 0.01, 0.07, 0.05, 0.05
        sub_fraction = (1 - bottom_space - k_fraction -
                        vol_fraction - blank * 3) / 2
        axk = fig.add_axes([left_space, 1 - k_fraction, 1 -
                            left_space - right_space, k_fraction - top_space])
        axv = fig.add_axes([left_space, bottom_space, 1 -
                            left_space - right_space, vol_fraction], sharex=axk)
        ax0 = fig.add_axes([left_space, bottom_space + vol_fraction +
                            blank, 1 - left_space - right_space, sub_fraction], sharex=axk)
        ax1 = fig.add_axes([left_space, bottom_space + vol_fraction + sub_fraction +
                            2 * blank, 1 - left_space - right_space, sub_fraction], sharex=axk)
        plt.setp(ax0.get_xticklabels(), visible=False)
        plt.setp(ax1.get_xticklabels(), visible=False)
        ax0.set_ylabel(ylabel=plot_lt[0][0], fontdict={'fontsize': 'x-small'})
        ax1.set_ylabel(ylabel=plot_lt[0][1], fontdict={'fontsize': 'x-small'})
        ax0.set_facecolor(axk_color)
        ax1.set_facecolor(axv_color)
        plot_indicator(ax0, plot_lt[0][0])
        plot_indicator(ax1, plot_lt[0][1])
    axk.set_facecolor(axk_color)
    axv.set_facecolor(axv_color)
    plt.setp(axk.get_xticklabels(), visible=False)
    plt.setp(axv.get_xticklabels(), visible=True)
    axk.set_ylabel(ylabel='Price', fontdict={'fontsize': 'small'})
    axv.set_ylabel(ylabel='Vol', fontdict={'fontsize': 'small'})
    axv.tick_params(axis='x', labelsize='small')
    axv.tick_params(axis='y', labelsize='small')
    axk.tick_params(axis='y', labelsize='small')
    axv.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    axk.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    axv.xaxis.set_major_locator(
        locator=ticker.MultipleLocator(len(time_lt) // 7))
    axk.xaxis.set_major_locator(
        locator=ticker.MultipleLocator(len(time_lt) // 7))
    candlestick_ohlc(axk, data_lt, width=0.6, colorup='#e01055',
                     colordown='#008c64', alpha=1)
    df['closechg'] = df['close'].diff()
    df['closechg'].fillna(0, inplace=True)
    df['red vol'] = np.where(df['closechg'] > 0, df['vol'], 0)
    df['orange vol'] = np.where(df['closechg'] == 0, df['vol'], 0)
    df['green vol'] = np.where(df['closechg'] < 0, df['vol'], 0)
    axv.bar(time_lt, df[start_idx:last_idx + 1]['red vol'], width=0.6,
            linewidth=0, color='#cc0022', alpha=1, label='vol')
    axv.bar(time_lt, df[start_idx:last_idx + 1]['orange vol'], width=0.6,
            linewidth=0, color='#f28100', alpha=1, label='vol')
    axv.bar(time_lt, df[start_idx:last_idx + 1]['green vol'], width=0.6,
            linewidth=0, color='#00804b', alpha=1, label='vol')

    if chk_lt[1] == 1:
        df['mama'], df['fama'] = talib.MAMA(
            df['close'], fastlimit=plot_lt[0][2], slowlimit=plot_lt[0][3])
        axk.plot(time_lt, df[start_idx:last_idx + 1]['mama'],
                 label='MAMA', color=mavcolors[-2], linewidth=0.7)
        axk.plot(time_lt, df[start_idx:last_idx + 1]['fama'],
                 label='FAMA', color=mavcolors[-1], linewidth=0.7)
        axk.fill_between(time_lt, df[start_idx:last_idx + 1]['mama'], df[start_idx:last_idx + 1]['fama'],
                         where=df[start_idx:last_idx + 1]['mama'] > df[start_idx:last_idx + 1]['fama'], color='#FF44AA',
                         alpha=0.5)  # 多
        axk.fill_between(time_lt, df[start_idx:last_idx + 1]['mama'], df[start_idx:last_idx + 1]['fama'],
                         where=df[start_idx:last_idx + 1]['mama'] < df[start_idx:last_idx + 1]['fama'], color='#0b7356',
                         alpha=0.5)  # 空
    if chk_lt[2] == 1:
        df['ht'] = talib.HT_TRENDLINE(df['close'])
        axk.plot(time_lt, df[start_idx:last_idx + 1]['ht'],
                 label='HT trendline', color='#fa8b02', linewidth=0.7)  # fa8b02
        axk.fill_between(time_lt, df[start_idx:last_idx + 1]['ht'], df[start_idx:last_idx + 1]['close'],
                         where=df[start_idx:last_idx +
                                  1]['close'] > df[start_idx:last_idx + 1]['ht'],
                         color='#0cb5f2',
                         alpha=0.5)  # 多
        axk.fill_between(time_lt, df[start_idx:last_idx + 1]['ht'], df[start_idx:last_idx + 1]['close'],
                         where=df[start_idx:last_idx +
                                  1]['close'] < df[start_idx:last_idx + 1]['ht'],
                         color='#ffea00',
                         alpha=0.5)  # 空
    if type(a) == type(b) == int and a != b:
        n_tup = (a, b)
        hma_colors = (('#e30048', '#00d423'),
                      ('#e08402', '#00ccc9'))
        for hma_i, n in enumerate(n_tup):
            half_n = int(round(n / 2, 0))
            root_n = int(round(pow(n, 0.5), 0))
            c_copy = pd.DataFrame({'close': []})
            hma_1 = 2 * abstract.WMA(df, half_n)
            hma_2 = abstract.WMA(df, n)
            c_copy['close'] = hma_1 - hma_2
            col = 'hma' + str(n)
            df[col] = abstract.WMA(c_copy, root_n)
            df[col + 'd'] = df[col].diff()
            df['up-' + col] = np.where(df[col + 'd'] > 0, df[col], np.NaN)
            df['down-' + col] = np.where(df[col + 'd']
                                         <= 0, df[col], np.NaN)
            axk.scatter(time_lt, df[start_idx:last_idx + 1]['up-' + col], label=col + '(上升)',
                        color=hma_colors[hma_i][0], s=2)
            axk.scatter(time_lt, df[start_idx:last_idx + 1]['down-' + col], label=col + '(下降)', color=hma_colors[hma_i][1],
                        s=2)
    all_ma_lt, k1 = [], 0
    for num, ma_day in enumerate(plot_lt[1]):
        ma_type = plot_lt[2][num]
        if type(ma_day) == int and ma_type != '無' and (ma_day, ma_type) not in all_ma_lt:
            all_ma_lt.append((ma_day, ma_type))
            ma_label = str(ma_day) + ma_type
            df[ma_label] = abstract.MA(
                df, timeperiod=ma_day, matype=matype_dict[ma_type])
            axk.plot(time_lt, df[start_idx:last_idx + 1][ma_label], label=ma_label, color=mavcolors[k1],
                     linewidth=0.6)
            k1 += 1
    if type(plot_lt[3][0]) == int and plot_lt[3][1] != '無' and (plot_lt[3][2] != '無' or plot_lt[3][3] != '無' or plot_lt[3][4] != '無'):
        bb_color = ['#FF1493', '#FF69B4', '#FFB6C1']
        for e, dev in enumerate(plot_lt[3][2:]):
            if dev != '無' and dev != '':
                upperband, middleband, lowerband = talib.BBANDS(df['close'],
                                                                timeperiod=plot_lt[3][0], nbdevup=dev, nbdevdn=dev,
                                                                matype=matype_dict[plot_lt[3][1]])
                if e == 0 and (all_ma_lt == [] or (plot_lt[3][0], plot_lt[3][1]) not in all_ma_lt):
                    df['midband'] = middleband
                    axk.plot(time_lt, df[start_idx:last_idx + 1]['midband'], color=bb_color[e],
                             linewidth=0.5, linestyle='dashed', label='布林中軌({:n}{})'.format(plot_lt[3][0], '日'))
                df['upband' + str(dev)] = upperband
                df['lowband' + str(dev)] = lowerband
                axk.plot(time_lt, df[start_idx:last_idx + 1]['upband' + str(dev)], color=bb_color[e], linewidth=0.5,
                         linestyle='dashed', label='{}倍標準差'.format(str(dev)))
                axk.plot(time_lt, df[start_idx:last_idx + 1]['lowband' + str(dev)], color=bb_color[e], linewidth=0.5,
                         linestyle='dashed')
    axk.legend(framealpha=0, markerscale=0.8, fontsize='x-small')
    name = code_dict[code] if code in code_dict else code
    axk.set_title(label=name + '（' + str(code) + '）',
                  fontdict={'fontsize': 'small'})
    if file != 0:
        if file[-5] == 'b':
            for num, trade in enumerate(trade_lt, start=1):
                low_idx, high_idx = df[df['date'] == trade[0]
                                       ].index, df[df['date'] == trade[2]].index
                low, high = df.loc[low_idx, 'low'], df.loc[high_idx, 'high']
                buy_date = trade[0].strftime('%Y-%m-%d')
                sell_date = trade[2].strftime('%Y-%m-%d')
                cp_ratio = round(100 * (trade[3] / trade[1] - 1), 1)
                color_tup = ('#b31522', '#e60b1d') if cp_ratio > 0 else (
                    '#02a876', '#2cdba7')
                axk.annotate(text='b' + str(num), xy=(buy_date, low * 0.99), xytext=(0, -15),
                             textcoords='offset points', arrowprops={'arrowstyle': '->', 'facecolor': color_tup[1], 'edgecolor': color_tup[1]},
                             annotation_clip=False, color=color_tup[0])
                axk.annotate(text='s' + str(num) + ':' + str(cp_ratio) + '%', xy=(sell_date, high * 1.01), xytext=(0, 10),
                             textcoords='offset points', arrowprops={'arrowstyle': '->', 'facecolor': color_tup[1], 'edgecolor': color_tup[1]},
                             annotation_clip=False, color=color_tup[0])
        else:
            for num, trade in enumerate(trade_lt, start=1):
                low_idx, high_idx = df[df['date'] == trade[2]
                                       ].index, df[df['date'] == trade[0]].index
                low, high = df.loc[low_idx, 'low'], df.loc[high_idx, 'high']
                sell_date = trade[0].strftime('%Y-%m-%d')
                buy_date = trade[2].strftime('%Y-%m-%d')
                cp_ratio = round(100 * (trade[1] / trade[3] - 1), 1)
                color_tup = ('#b31522', '#e60b1d') if cp_ratio > 0 else (
                    '#02a876', '#2cdba7')
                axk.annotate('s' + str(num), xy=(sell_date, high * 1.01), xytext=(0, 10),
                             textcoords='offset points', arrowprops={'arrowstyle': '->', 'facecolor': color_tup[1], 'edgecolor': color_tup[1]}, annotation_clip=False, color=color_tup[0])
                axk.annotate('b' + str(num) + ':' + str(cp_ratio) + '%', xy=(buy_date, low * 0.99), xytext=(0, -15),
                             textcoords='offset points', arrowprops={'arrowstyle': '->', 'facecolor': color_tup[1], 'edgecolor': color_tup[1]}, annotation_clip=False, color=color_tup[0])
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()
    return 0


"""
ShowAnnotationWithHMA('2337', dfname[0], [1, 0, 0], [['NATR', 'DMI', '0.66', '0.03'], [
                      '無', '無', 21, 55], ['EMA', 'EMA', 'EMA', 'EMA'], ['無', 'EMA', 2.0, 2.2, 3.0]], 9, 16)
"""
ExtraPlot('3374', 0, [1, 0, 0], [['NATR', 'DMI', '0.66', '0.03'], ['無', '無', 21, 55], [
          'EMA', 'EMA', 'EMA', 'EMA'], ['無', 'EMA', 2.0, 2.2, 3.0]], 9, 9, 'p')
