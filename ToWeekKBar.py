import csv
import pandas as pd
import numpy as np
from os import listdir
from datetime import timedelta, datetime
file_lt = listdir('D:/2016_2019/p')


def RecFeatures(file, n):
    df = pd.read_csv(file, parse_dates=['buy_date', 'sell_date'])
    new_cols = ['vol1max>2min', 'vol2max>2min', 'vol3max>2min', 'vol4max>2min',
                'vol1max>2med', 'vol2max>2med', 'vol3max>2med', 'vol4max>2med',
                'vol1max', 'vol2max', 'vol3max', 'vol4max',
                'lowshadow1', 'lowshadow2', 'lowshadow3', 'lowshadow4',
                'low1', 'low2', 'low3', 'low4',
                'high1', 'high2', 'high3', 'high4']
    for col in new_cols:
        df[col] = np.zeros(len(df))
    done_code = list(set(df['code'].values))
    done_code.sort()
    done_code = [int(code) for code in done_code]
    for code in done_code:
        print(code)
        codef = df[df['code'] == code]
        wk_df = pd.read_csv('D:/2016_2019/weekp/w' +
                            str(code) + '.csv', parse_dates=['date'])
        idx_lt = codef.index.to_list()
        for df_i in idx_lt:
            date = codef.loc[df_i, 'buy_date']
            wk_idx = wk_df[wk_df['date'] == date].index.to_list()[0]
            pass_i = wk_idx - 4
            if pass_i >= 0:
                vol = wk_df.loc[pass_i + 3, 'maxv']

                """
                half_n = int(round(n / 2, 0))
                root_n = int(round(pow(n, 0.5), 0))
                c_copy = pd.DataFrame({'close': []})
                hma_1 = 2 * abstract.WMA(wk_df, half_n)
                hma_2 = abstract.WMA(wk_df, n)
                c_copy['close'] = hma_1 - hma_2
                wk_df['HMA-' + str(n)] = abstract.WMA(c_copy, root_n)
                hma6 = wk_df.loc[pass_i, 'HMA-' + str(n)]
                for col in new_cols:
                    df.loc[df_i, col] = wk_df.loc[wk_idx -
                                                  int(col[3:]), 'HMA-' + str(n)] / hma6
                """
    df.to_csv(file, index=False)
    print('done', file)


def ToMonthKBar(code):
    df = pd.read_csv('D:/2016_2019/p/p' + code +
                     '.csv', parse_dates=['date'])
    df.sort_values(by=['date'], inplace=True, ignore_index=True)
    ori_len = len(df)
    wd_lt, temp_lt, mon_dict = [], [], {
        'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'vol': [], 'days': []}
    df.loc[ori_len] = [df.loc[ori_len - 1, 'date'] +
                       timedelta(days=31), 0, 0, 0, 0, 0]
    for i in range(ori_len):
        tdy, next_day = df.loc[i, 'date'], df.loc[i + 1, 'date']
        tdy_mon = tdy.strftime('%Y%m')
        next_mon = next_day.strftime('%Y%m')
        temp_lt.append(i)
        if next_mon != tdy_mon:
            wd_lt.append(temp_lt)
            temp_lt = []
    for wk in wd_lt:
        mon_dict['date'].append(df.loc[wk[0], 'date'])
        mon_dict['open'].append(df.loc[wk[0], 'open'])
        high_lt, low_lt, vol_lt = [], [], []
        for idx in wk:
            high_lt.append(df.loc[idx, 'high'])
            low_lt.append(df.loc[idx, 'low'])
            vol_lt.append(df.loc[idx, 'vol'])
        mon_dict['high'].append(max(high_lt))
        mon_dict['low'].append(min(low_lt))
        mon_dict['close'].append(df.loc[wk[-1], 'close'])
        mon_dict['vol'].append(sum(vol_lt))
        mon_dict['days'].append(len(wk))
    wk_df = pd.DataFrame(mon_dict)
    wk_df.to_csv('D:/2016_2019/monp/m' + code + '.csv', index=False)


def ToWeekKBar(code):
    print(code)
    df = pd.read_csv('D:/2016_2019/p/p' + code +
                     '.csv', parse_dates=['date'])
    #df.sort_values(by=['date'], inplace=True, ignore_index=True)
    ori_len = len(df)
    wd_lt, temp_lt, week_dict = [], [], {
        'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'vol': [], 'days': [], 'maxv': [], 'medv': [], 'minv': [], 'maxidx': [], 'minidx': []}
    df.loc[ori_len] = [df.loc[ori_len - 1, 'date'] +
                       timedelta(days=6), 0, 0, 0, 0, 0]
    for i in range(ori_len):
        tdy, next_day = df.loc[i, 'date'], df.loc[i + 1, 'date']
        tdy_wd = tdy.isoweekday()
        next_wd = next_day.isoweekday()
        temp_lt.append(i)
        if next_wd <= tdy_wd or (next_day - tdy).days > 5:
            wd_lt.append(temp_lt)
            temp_lt = []
    for wk in wd_lt:
        week_dict['date'].append(df.loc[wk[0], 'date'])
        week_dict['open'].append(df.loc[wk[0], 'open'])
        high_lt, low_lt, vol_lt = [], [], []
        for idx in wk:
            high_lt.append(df.loc[idx, 'high'])
            low_lt.append(df.loc[idx, 'low'])
            vol_lt.append(df.loc[idx, 'vol'])
        week_dict['high'].append(max(high_lt))
        week_dict['low'].append(min(low_lt))
        week_dict['close'].append(df.loc[wk[-1], 'close'])
        week_dict['vol'].append(sum(vol_lt))
        week_dict['days'].append(len(wk))
        week_dict['maxv'].append(max(vol_lt))
        week_dict['medv'].append(np.median(vol_lt))
        week_dict['minv'].append(min(vol_lt))
        week_dict['maxidx'].append(np.argmax(vol_lt))
        week_dict['minidx'].append(np.argmin(vol_lt))

    wk_df = pd.DataFrame(week_dict)
    wk_df.to_csv('D:/2016_2019/weekp/w' + code + '.csv', index=False)


with open('D:/stocks/tdy_done.txt', newline='\n', encoding='utf-8') as tdyf:
    tdy_done = list(csv.reader(tdyf))[-1][0]
with open('D:/stocks/weekp_done.txt', newline='\n', encoding='utf-8') as wdonef:
    wk_date = list(csv.reader(wdonef))[-1][0]
dt_tdy_done = pd.to_datetime(tdy_done, format='%Y%m%d')
dt_wkp = pd.to_datetime(wk_date, format='%Y%m%d')
isowk_tdy = dt_tdy_done.isoweekday()
day_delta = isowk_tdy - 1
last_Monday = dt_tdy_done - timedelta(days=day_delta)
print(dt_wkp, last_Monday)
if dt_wkp < last_Monday:
    print('weekp not done yet')
    for f in file_lt:
        ToWeekKBar(f[1:5])
    dt_str = last_Monday.strftime('%Y%m%d')
    with open('D:/stocks/weekp_done.txt', 'a', newline='\n', encoding='utf-8') as wdonef:
        wr = csv.writer(wdonef)
        wr.writerow([dt_str])
else:
    print('Weekp done')
