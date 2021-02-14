import csv
# sys.path.append(r'C:\Users\user\PycharmProjects\stocks\venv\Lib\site-packages')
import pandas as pd
import numpy as np
from talib import abstract
import talib
from datetime import timedelta
min_date, end, mode_dict = pd.to_datetime('20100125', format='%Y%m%d'), pd.to_datetime(
    '20000101', format='%Y%m%d'), {'backtest': -2, 'select': 1}
min_idx, max_len, out_mode, min_week, max_wk = 109, 89, {
    'backtest': (1, 'open'), 'select': (0, 'close')}, 21, 18
with open('D:/stocks/BullCol.txt', newline='\n', encoding='utf-8') as bullf:
    bull_columns = list(csv.reader(bullf))[0]
with open('D:/stocks/BearCol.txt', newline='\n', encoding='utf-8') as bearf:
    bear_columns = list(csv.reader(bearf))[0]
# stk_array=array[code, start_date, start_p, end_date, end_p]


def ToWeekKBar(code, mode):
    df = pd.read_csv('D:/2016_2019/p/p' + code +
                     '.csv', parse_dates=['date'])
    df.sort_values(by=['date'], inplace=True, ignore_index=True)
    ori_len = len(df)
    wd_lt, temp_lt, week_dict = [], [], {
        'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'vol': []}
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
    wk_df = pd.DataFrame(week_dict)
    if code != '1000':
        wk_df['amt'] = wk_df['vol'] * \
            (2 * wk_df['close'] + wk_df['high'] + wk_df['low']) / 4
    else:
        wk_df['amt'] = wk_df['vol'] * 10 ** 5
    wk_df['max4amt'] = wk_df['amt'].rolling(4, min_periods=4).max()
    wk_df['DI+'] = abstract.PLUS_DI(wk_df, timeperiod=14)
    wk_df['DI-'] = abstract.MINUS_DI(wk_df, timeperiod=14)

    upperband, middleband, lowerband = talib.BBANDS(wk_df['close'], timeperiod=21, nbdevup=2.1, nbdevdn=2.1,
                                                    matype=1)
    wk_df['upband'] = upperband
    wk_df['lowband'] = lowerband
    wk_df['bandwidth'] = upperband / lowerband - 1
    wk_df['slowk13'], wk_df['slowd13'] = talib.STOCH(
        wk_df['high'], wk_df['low'], wk_df['close'], fastk_period=13, slowk_period=3, slowk_matype=1, slowd_period=3, slowd_matype=1)
    fst_idx = [ind for ind in wk_df[wk_df['date'] >= min_date].index.to_list(
    ) if ind >= min_week][0] if mode == 'backtest' else len(wk_df) - 1
    return wk_df.loc[fst_idx - max_wk:]
    #wk_df.to_csv('D:/2016_2019/weekp/w' + code + '.csv', index=False)


def CalFeature(df, stk_array, id, direction):
    non_float32 = np.array(
        ['code', 'buy_date', 'sell_date', 'buy_p', 'sell_p'])
    stk_array = np.append(stk_array, [df.loc[id, var2] for var2 in (
        'DI+', 'DI-', 'slowk13', 'slowd13', 'bandwidth')])
    stk_array = np.append(
        stk_array, [df.loc[id, 'bandwidth'] / df.loc[id - 1, 'bandwidth'] - 1])
    stk_df = pd.DataFrame([stk_array], index=[
                          0], columns=bull_columns if direction == 'bull' else bear_columns)
    stk_df = stk_df.astype(
        {k: 'float32' for k in stk_df.columns if k not in non_float32})
    return stk_df


def ExeTA(code, mode):
    pr_df = pd.read_csv('D:/2016_2019/p/p' + code +
                        '.csv', parse_dates=['date'])
    idx_lt = pr_df.tail(1).index.to_list()
    if len(idx_lt) != 0:
        pr_df['ema5'] = abstract.EMA(pr_df, timeperiod=5)
        pr_df['ema13'] = abstract.EMA(pr_df, timeperiod=13)
        pr_df['ema21'] = abstract.EMA(pr_df, timeperiod=21)
        pr_df['ema55'] = abstract.EMA(pr_df, timeperiod=55)
        pr_df['mv21'] = pr_df['vol'].rolling(21, min_periods=21).mean()
        macd9 = abstract.MACDEXT(pr_df, fastperiod=12, fastmatype=1,
                                 slowperiod=26, slowmatype=1,
                                 signalperiod=9, signalmatype=1)
        if code != '1000':
            pr_df['amt'] = pr_df['vol'] * \
                (2 * pr_df['close'] + pr_df['high'] + pr_df['low']) / 4
        else:
            pr_df['amt'] = pr_df['vol'] * 10 ** 5
        pr_df['mm21'] = pr_df['amt'].rolling(21, min_periods=21).mean()
        pr_df['macdhist'] = macd9['macdhist']
        upperband, middleband, lowerband = talib.BBANDS(pr_df['close'], timeperiod=21, nbdevup=2.1, nbdevdn=2.1,
                                                        matype=1)
        pr_df['upband'] = upperband
        pr_df['lowband'] = lowerband
        pr_df['bandwidth'] = upperband / lowerband - 1
        pr_df['DI+'] = abstract.PLUS_DI(pr_df, timeperiod=14)
        pr_df['DI-'] = abstract.MINUS_DI(pr_df, timeperiod=14)
        pr_df['slowk13'], pr_df['slowd13'] = talib.STOCH(
            pr_df['high'], pr_df['low'], pr_df['close'], fastk_period=13, slowk_period=3, slowk_matype=1, slowd_period=3, slowd_matype=1)
        fst_idx = [ind for ind in pr_df[pr_df['date'] >= min_date].index.to_list(
        ) if ind >= min_idx][0] if mode == 'backtest' else len(pr_df) - 1
        """
        with open('D:/stocks/ExeTA_done.txt', 'a', newline='\n', encoding='utf-8') as tadone:
            wr = csv.writer(tadone)
            wr.writerow(
                [code + '-' + pr_df.loc[last_idx, 'date'].strftime('%Y%m%d')])
        """
        return pr_df.loc[fst_idx - max_len:]
    else:
        raise IndexError


def NoTrade():
    return 0


def ReachTop(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=2, b=0.08, c=0.08, d=0, e=0.05, f=0.08, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('D:/stocks/BullCol.csv').astype({'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv(
        'D:/stocks/BearCol.csv').astype({'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ExeTA(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_len, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if action == 'BearIn':
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                upband_0 = pr_df.loc[i, 'upband']
                upband_1 = pr_df.loc[i - 1, 'upband']
                upband_13 = pr_df.loc[i - 13, 'upband']
                lowband_0 = pr_df.loc[i, 'lowband']
                lowband_1 = pr_df.loc[i - 1, 'lowband']
                lowband_13 = pr_df.loc[i - 13, 'lowband']
                width_0 = pr_df.loc[i, 'bandwidth']
                width_1 = pr_df.loc[i - 1, 'bandwidth']
                width_13 = pr_df.loc[i - 13, 'bandwidth']
                high_0 = pr_df.loc[i, 'high']
                close_0 = pr_df.loc[i, 'close']
                volume_0 = pr_df.loc[i, 'vol']
                mv21_0 = pr_df.loc[i, 'mv21']
                cond01 = high_0 >= upband_0 and close_0 <= upband_0 and volume_0 <= a * \
                    mv21_0 and width_0 >= b and width_13 >= c and upband_0 / upband_1 - \
                    1 <= d and upband_0 / upband_13 - 1 <= e and width_1 >= f
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bear_record = bear_record.append(CalFeature(pr_df, np.array([int(code), pr_df.loc[i + 1, 'date'], float(
                        pr_df.loc[i + 1, 'open']), end, 0, pr_df.loc[i, 'amt']]), i, 'bear'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bear_record = bear_record.append(CalFeature(pr_df, np.array([int(code), pr_df.loc[i, 'date'], float(
                        pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]), i, 'bear'), ignore_index=True, sort=False)
        return bear_record
    elif action == 'BearOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                upband_0 = pr_df.loc[i, 'upband']
                upband_1 = pr_df.loc[i - 1, 'upband']
                upband_13 = pr_df.loc[i - 13, 'upband']
                lowband_0 = pr_df.loc[i, 'lowband']
                lowband_1 = pr_df.loc[i - 1, 'lowband']
                lowband_13 = pr_df.loc[i - 13, 'lowband']
                width_0 = pr_df.loc[i, 'bandwidth']
                width_1 = pr_df.loc[i - 1, 'bandwidth']
                width_13 = pr_df.loc[i - 13, 'bandwidth']
                high_0 = pr_df.loc[i, 'high']
                close_0 = pr_df.loc[i, 'close']
                volume_0 = pr_df.loc[i, 'vol']
                mv21_0 = pr_df.loc[i, 'mv21']
                cond01 = high_0 >= upband_0 and close_0 <= upband_0 and volume_0 <= a * \
                    mv21_0 and width_0 >= b and width_13 >= c and upband_0 / upband_1 - \
                    1 <= d and upband_0 / upband_13 - 1 <= e and width_1 >= f
                if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -BearTP or (cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                    sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bear_record
    elif action == 'BullIn':
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                upband_0 = pr_df.loc[i, 'upband']
                upband_1 = pr_df.loc[i - 1, 'upband']
                upband_13 = pr_df.loc[i - 13, 'upband']
                lowband_0 = pr_df.loc[i, 'lowband']
                lowband_1 = pr_df.loc[i - 1, 'lowband']
                lowband_13 = pr_df.loc[i - 13, 'lowband']
                width_0 = pr_df.loc[i, 'bandwidth']
                width_1 = pr_df.loc[i - 1, 'bandwidth']
                width_13 = pr_df.loc[i - 13, 'bandwidth']
                high_0 = pr_df.loc[i, 'high']
                close_0 = pr_df.loc[i, 'close']
                volume_0 = pr_df.loc[i, 'vol']
                mv21_0 = pr_df.loc[i, 'mv21']
                cond01 = high_0 >= upband_0 and close_0 <= upband_0 and volume_0 <= a * \
                    mv21_0 and width_0 >= b and width_13 >= c and upband_0 / upband_1 - \
                    1 <= d and upband_0 / upband_13 - 1 <= e and width_1 >= f
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bull_record = bull_record.append(CalFeature(pr_df, np.array([int(code), pr_df.loc[i + 1, 'date'], float(
                        pr_df.loc[i + 1, 'open']), end, 0, pr_df.loc[i, 'amt']]), i, 'bull'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bull_record = bull_record.append(CalFeature(pr_df, np.array([int(code), pr_df.loc[i, 'date'], float(
                        pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]), i, 'bull'), ignore_index=True, sort=False)
        return bull_record
    else:
        for data_i in range(len(sent_bull_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                upband_0 = pr_df.loc[i, 'upband']
                upband_1 = pr_df.loc[i - 1, 'upband']
                upband_13 = pr_df.loc[i - 13, 'upband']
                lowband_0 = pr_df.loc[i, 'lowband']
                lowband_1 = pr_df.loc[i - 1, 'lowband']
                lowband_13 = pr_df.loc[i - 13, 'lowband']
                width_0 = pr_df.loc[i, 'bandwidth']
                width_1 = pr_df.loc[i - 1, 'bandwidth']
                width_13 = pr_df.loc[i - 13, 'bandwidth']
                high_0 = pr_df.loc[i, 'high']
                close_0 = pr_df.loc[i, 'close']
                volume_0 = pr_df.loc[i, 'vol']
                mv21_0 = pr_df.loc[i, 'mv21']
                cond01 = high_0 >= upband_0 and close_0 <= upband_0 and volume_0 <= a * \
                    mv21_0 and width_0 >= b and width_13 >= c and upband_0 / upband_1 - \
                    1 <= d and upband_0 / upband_13 - 1 <= e and width_1 >= f
                if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= BullTP or (cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                    sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                  out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bull_record


def MacdNegHistConverge(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=2, b=0.08, c=0.08, d=0, e=0.05, f=0.08, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('BullCol.csv').astype({'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv(
        'BearCol.csv').astype({'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ExeTA(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_len, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if action == 'BearOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                hist_0 = pr_df.loc[i, 'macdhist']
                hist_1 = pr_df.loc[i - 1, 'macdhist']
                hist_2 = pr_df.loc[i - 2, 'macdhist']
                close_0 = pr_df.loc[i, 'close']
                cond01 = hist_1 < hist_2 and hist_1 < 0 and hist_0 > hist_1
                if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / sent_bear_record.loc[
                    data_i, 'sell_p'] - 1 <= -BearTP or (
                        cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                    sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bear_record
    elif action == 'BearIn':
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                hist_0 = pr_df.loc[i, 'macdhist']
                hist_1 = pr_df.loc[i - 1, 'macdhist']
                hist_2 = pr_df.loc[i - 2, 'macdhist']
                cond01 = hist_1 < hist_2 and hist_1 < 0 and hist_0 > hist_1
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bear_record = bear_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0, pr_df.loc[i, 'amt']]),
                        i, 'bear'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bear_record = bear_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]), i,
                        'bear'), ignore_index=True, sort=False)
        return bear_record
    elif action == 'BullOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                hist_0 = pr_df.loc[i, 'macdhist']
                hist_1 = pr_df.loc[i - 1, 'macdhist']
                hist_2 = pr_df.loc[i - 2, 'macdhist']
                close_0 = pr_df.loc[i, 'close']
                cond01 = hist_1 < hist_2 and hist_1 < 0 and hist_0 > hist_1
                if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= BullTP or (cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                    sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                  out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bull_record
    else:
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                hist_0 = pr_df.loc[i, 'macdhist']
                hist_1 = pr_df.loc[i - 1, 'macdhist']
                hist_2 = pr_df.loc[i - 2, 'macdhist']
                cond01 = hist_1 < hist_2 and hist_1 < 0 and hist_0 > hist_1
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bull_record = bull_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0, pr_df.loc[i, 'amt']]),
                        i, 'bull'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bull_record = bull_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]), i,
                        'bull'), ignore_index=True, sort=False)
        return bull_record


def CrossOverTangledMA(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=1.5, b=0.03, c=0.01, d=0.005, e=0.05, f=0.01, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('BullCol.csv').astype({'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv(
        'BearCol.csv').astype({'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ExeTA(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_len, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if action == 'BullIn':
        for i in range(fst_idx, last_idx):
            ma55_5, ma21_5, ma13_5, ma5_5 = pr_df.loc[i - 5, 'ema55'], pr_df.loc[i - 5, 'ema21'], pr_df.loc[
                i - 5, 'ema13'], pr_df.loc[i - 5, 'ema5']
            ma55_0, ma21_0 = pr_df.loc[i, 'ema55'], pr_df.loc[i, 'ema21']
            max_ma_5 = max(ma21_5, ma13_5, ma5_5)
            min_ma_5 = min(ma21_5, ma13_5, ma5_5)
            tangled_ma = max_ma_5 / min_ma_5 - 1 <= c
            close_0, close_1, close_2 = pr_df.loc[i,
                                                  'close'], pr_df.loc[i - 1, 'close'], pr_df.loc[i - 2, 'close']
            high_1 = pr_df.loc[i - 1, 'high']
            open_0 = pr_df.loc[i, 'open']
            mon_amt = pr_df.loc[i, 'mm21']
            volume_0 = pr_df.loc[i, 'vol']
            mv21_0 = pr_df.loc[i, 'mv21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt and tangled_ma:
                if close_2 < min_ma_5:
                    cond01 = close_0 >= high_1 and close_0 / open_0 - 1 >= b and close_0 / close_1 - 1 >= b and volume_0 >= mv21_0 * \
                        a and ma55_0 >= ma55_5 * \
                        (1 + d) and ma21_0 >= ma55_0 * \
                        (1 + e) and ma21_0 >= ma21_5 * (1 + f)
                    if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                        bull_record = bull_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                             pr_df.loc[i, 'amt']]),
                            i, 'bull'), ignore_index=True, sort=False)
                    elif cond01 and mode == 'select':
                        bull_record = bull_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                            i,
                            'bull'), ignore_index=True, sort=False)
        return bull_record
    elif action == 'BullOut':
        for data_i in range(len(sent_bull_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                ma55_5, ma21_5, ma13_5, ma5_5 = pr_df.loc[i - 2, 'ema55'], pr_df.loc[i -
                                                                                     2, 'ema21'], pr_df.loc[i - 2, 'ema13'], pr_df.loc[i - 2, 'ema5']
                ma55_0, ma21_0 = pr_df.loc[i, 'ema55'], pr_df.loc[i, 'ema21']
                max_ma_5 = max(ma21_5, ma13_5, ma5_5)
                min_ma_5 = min(ma21_5, ma13_5, ma5_5)
                tangled_ma = max_ma_5 / min_ma_5 - 1 <= c
                close_0, close_1, close_2 = pr_df.loc[i, 'close'], pr_df.loc[i - 1, 'close'], pr_df.loc[
                    i - 2, 'close']
                high_1 = pr_df.loc[i - 1, 'high']
                open_0 = pr_df.loc[i, 'open']
                volume_0 = pr_df.loc[i, 'vol']
                mv21_0 = pr_df.loc[i, 'mv21']
                if tangled_ma:
                    if close_2 < min_ma_5:
                        cond01 = close_0 >= high_1 and close_0 / open_0 - 1 >= b and close_0 / close_1 - 1 >= b and volume_0 >= mv21_0 * a and ma55_0 >= ma55_5 * (
                            1 + d) and ma21_0 >= ma55_0 * (1 + e) and ma21_0 >= ma21_5 * (1 + f)
                        if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / \
                                sent_bull_record.loc[data_i, 'buy_p'] - 1 >= BullTP or (
                                cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                            sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                          out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                            break
        return sent_bull_record
    elif action == 'BearIn':
        for i in range(fst_idx, last_idx):
            ma55_5, ma21_5, ma13_5, ma5_5 = pr_df.loc[i - 2, 'ema55'], pr_df.loc[i - 2, 'ema21'], pr_df.loc[
                i - 2, 'ema13'], pr_df.loc[i - 2, 'ema5']
            ma55_0, ma21_0 = pr_df.loc[i, 'ema55'], pr_df.loc[i, 'ema21']
            max_ma_5 = max(ma21_5, ma13_5, ma5_5)
            min_ma_5 = min(ma21_5, ma13_5, ma5_5)
            tangled_ma = max_ma_5 / min_ma_5 - 1 <= c
            close_0, close_1, close_2 = pr_df.loc[i,
                                                  'close'], pr_df.loc[i - 1, 'close'], pr_df.loc[i - 2, 'close']
            high_1 = pr_df.loc[i - 1, 'high']
            open_0, volume_0, mv21_0 = pr_df.loc[i,
                                                 'open'], pr_df.loc[i, 'vol'], pr_df.loc[i, 'mv21']
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt and tangled_ma:
                if close_2 < min_ma_5:
                    cond01 = close_0 >= high_1 and close_0 / open_0 - 1 >= b and close_0 / close_1 - 1 >= b and volume_0 >= mv21_0 * a and ma55_0 >= ma55_5 * (
                        1 + d) and ma21_0 >= ma55_0 * (1 + e) and ma21_0 >= ma21_5 * (1 + f)
                    if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                        bear_record = bear_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                             pr_df.loc[i, 'amt']]),
                            i, 'bear'), ignore_index=True, sort=False)
                    elif cond01 and mode == 'select':
                        bear_record = bear_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                            i,
                            'bear'), ignore_index=True, sort=False)
        return bear_record
    else:
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                ma55_5, ma21_5, ma13_5, ma5_5 = pr_df.loc[i - 2, 'ema55'], pr_df.loc[i - 2, 'ema21'], pr_df.loc[
                    i - 2, 'ema13'], pr_df.loc[i - 2, 'ema5']
                ma55_0, ma21_0 = pr_df.loc[i, 'ema55'], pr_df.loc[i, 'ema21']
                max_ma_5 = max(ma21_5, ma13_5, ma5_5)
                min_ma_5 = min(ma21_5, ma13_5, ma5_5)
                tangled_ma = max_ma_5 / min_ma_5 - 1 <= c
                close_0, close_1, close_2 = pr_df.loc[i, 'close'], pr_df.loc[i - 1, 'close'], pr_df.loc[
                    i - 2, 'close']
                high_1 = pr_df.loc[i - 1, 'high']
                open_0 = pr_df.loc[i, 'open']
                volume_0 = pr_df.loc[i, 'vol']
                mv21_0 = pr_df.loc[i, 'mv21']
                if tangled_ma:
                    if close_2 < min_ma_5:
                        cond01 = close_0 >= high_1 and close_0 / open_0 - 1 >= b and close_0 / close_1 - 1 >= b and volume_0 >= mv21_0 * a and ma55_0 >= ma55_5 * (
                            1 + d) and ma21_0 >= ma55_0 * (1 + e) and ma21_0 >= ma21_5 * (1 + f)
                        if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / \
                                sent_bear_record.loc[
                                data_i, 'sell_p'] - 1 <= -BearTP or (
                                cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                            sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                        out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                            break
        return sent_bear_record


def BreakThroughTangledMA(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=0.05, b=0.06, c=0.01, d=0.8, e=0.001, f=0.5, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('BullCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv('BearCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ExeTA(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_len, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if action == 'BullIn':
        for i in range(fst_idx, last_idx):
            ma55_0, ma21_0, ma13_0, ma5_0 = pr_df.loc[i, 'ema55'], pr_df.loc[i, 'ema21'], pr_df.loc[i, 'ema13'], pr_df.loc[
                i, 'ema5']
            ma21_1, ma5_1 = pr_df.loc[i - 1, 'ema21'], pr_df.loc[
                i - 1, 'ema5']
            max_ma_5 = max(ma21_0, ma13_0, ma5_0)
            min_ma_5 = min(ma21_0, ma13_0, ma5_0)
            tangled_ma = max_ma_5 / min_ma_5 - 1 <= a
            close_0, high_0 = pr_df.loc[i, 'close'], pr_df.loc[i, 'high']
            open_0, close_1, mon_amt, volume_0, mv21_0 = pr_df.loc[i, 'open'], pr_df.loc[i -
                                                                                         1, 'close'], pr_df.loc[i, 'mm21'], pr_df.loc[i, 'vol'], pr_df.loc[i, 'mv21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt and tangled_ma:
                cond01 = close_0 > max_ma_5 and close_0 >= open_0 and close_0 >= pr_df.loc[i - 5:i - 1]['high'].max() and b >= close_0 / close_1 - 1 >= c and ma5_0 > ma5_1 and ma21_0 > ma21_1 and (
                    high_0 == open_0 or (close_0 - open_0) / (high_0 - open_0) >= d) and close_0 / pr_df.loc[i - 89:i]['close'].min() - 1 <= e and volume_0 / mv21_0 - 1 >= f and ma21_0 > ma55_0
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bull_record = bull_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                         pr_df.loc[i, 'amt']]),
                        i, 'bull'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bull_record = bull_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                        i,
                        'bull'), ignore_index=True, sort=False)
        return bull_record
    elif action == 'BullOut':
        for data_i in range(len(sent_bull_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                ma55_0, ma21_0, ma13_0, ma5_0 = pr_df.loc[i, 'ema55'], pr_df.loc[i, 'ema21'], pr_df.loc[
                    i, 'ema13'], pr_df.loc[
                    i, 'ema5']
                ma21_1, ma5_1 = pr_df.loc[i - 1,
                                          'ema21'], pr_df.loc[i - 1, 'ema5']
                max_ma_5 = max(ma21_0, ma13_0, ma5_0)
                min_ma_5 = min(ma21_0, ma13_0, ma5_0)
                tangled_ma = max_ma_5 / min_ma_5 - 1 <= a
                close_0, high_0 = pr_df.loc[i, 'close'], pr_df.loc[
                    i, 'high']
                open_0, close_1, mon_amt, volume_0, mv21_0 = pr_df.loc[i, 'open'], pr_df.loc[i - 1, 'close'], \
                    pr_df.loc[i, 'mm21'], pr_df.loc[i, 'vol'], \
                    pr_df.loc[i, 'mv21']
                if tangled_ma:
                    cond01 = close_0 > max_ma_5 and close_0 >= open_0 and close_0 >= pr_df.loc[i - 5:i - 1]['high'].max() and b >= close_0 / close_1 - 1 >= c and ma5_0 > ma5_1 and ma21_0 > ma21_1 and (
                        high_0 == open_0 or (close_0 - open_0) / (high_0 - open_0) >= d) and close_0 / pr_df.loc[i - 89:i]['close'].min() - 1 <= e and volume_0 / mv21_0 - 1 >= f and ma21_0 > ma55_0
                    if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / sent_bull_record.loc[
                        data_i, 'buy_p'] - 1 >= BullTP or (
                            cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                        sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                      out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                        break
        return sent_bull_record
    elif action == 'BearIn':
        for i in range(fst_idx, last_idx):
            ma55_0, ma21_0, ma13_0, ma5_0 = pr_df.loc[i, 'ema55'], pr_df.loc[i, 'ema21'], pr_df.loc[i, 'ema13'], pr_df.loc[
                i, 'ema5']
            ma21_1, ma5_1 = pr_df.loc[i - 1, 'ema21'], pr_df.loc[i - 1, 'ema5']
            max_ma_5 = max(ma21_0, ma13_0, ma5_0)
            min_ma_5 = min(ma21_0, ma13_0, ma5_0)
            tangled_ma = max_ma_5 / min_ma_5 - 1 <= a
            close_0, high_0 = pr_df.loc[i, 'close'], pr_df.loc[
                i, 'high']
            open_0, close_1, mon_amt, volume_0, mv21_0 = pr_df.loc[i, 'open'], pr_df.loc[i - 1, 'close'], pr_df.loc[
                i, 'mm21'], pr_df.loc[i, 'vol'], pr_df.loc[i, 'mv21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt and tangled_ma:
                cond01 = close_0 > max_ma_5 and close_0 >= open_0 and close_0 >= pr_df.loc[i - 5:i - 1]['high'].max() and b >= close_0 / close_1 - 1 >= c and ma5_0 > ma5_1 and ma21_0 > ma21_1 and (
                    high_0 == open_0 or (close_0 - open_0) / (high_0 - open_0) >= d) and close_0 / pr_df.loc[i - 89:i]['close'].min() - 1 <= e and volume_0 / mv21_0 - 1 >= f and ma21_0 > ma55_0
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bear_record = bear_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                         pr_df.loc[i, 'amt']]),
                        i, 'bear'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bear_record = bear_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                        i,
                        'bear'), ignore_index=True, sort=False)
        return bear_record
    else:
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                ma55_0, ma21_0, ma13_0, ma5_0 = pr_df.loc[i, 'ema55'], pr_df.loc[i, 'ema21'], pr_df.loc[
                    i, 'ema13'], pr_df.loc[
                    i, 'ema5']
                ma21_1, ma5_1 = pr_df.loc[i - 1,
                                          'ema21'], pr_df.loc[i - 1, 'ema5']
                max_ma_5 = max(ma21_0, ma13_0, ma5_0)
                min_ma_5 = min(ma21_0, ma13_0, ma5_0)
                tangled_ma = max_ma_5 / min_ma_5 - 1 <= a
                close_0, high_0 = pr_df.loc[i, 'close'], pr_df.loc[
                    i, 'high']
                open_0, close_1, mon_amt, volume_0, mv21_0 = pr_df.loc[i, 'open'], pr_df.loc[i - 1, 'close'], \
                    pr_df.loc[
                    i, 'mm21'], pr_df.loc[i, 'vol'], pr_df.loc[i, 'mv21']
                if tangled_ma:
                    cond01 = close_0 > max_ma_5 and close_0 >= open_0 and close_0 >= pr_df.loc[i - 5:i - 1]['high'].max() and b >= close_0 / close_1 - 1 >= c and ma5_0 > ma5_1 and ma21_0 > ma21_1 and (
                        high_0 == open_0 or (close_0 - open_0) / (high_0 - open_0) >= d) and close_0 / pr_df.loc[i - 89:i]['close'].min() - 1 <= e and volume_0 / mv21_0 - 1 >= f and ma21_0 > ma55_0
                    if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / \
                            sent_bear_record.loc[
                            data_i, 'sell_p'] - 1 <= -BearTP or (
                            cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                        sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                    out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                        break
        return sent_bear_record


def FallBelow21EMA(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=-0.01, b=0.6, c=-0.01, d=1, e=-1, f=0.01, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('BullCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv('BearCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ExeTA(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_len, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if action == 'BullIn':
        for i in range(fst_idx, last_idx):
            ma21_0, ma21_1 = pr_df.loc[i, 'ema21'], pr_df.loc[i - 1, 'ema21']
            close_0, close_1 = pr_df.loc[i, 'close'], pr_df.loc[i - 1, 'close']
            low_0, high_0 = pr_df.loc[i, 'low'], pr_df.loc[i, 'high']
            mon_amt = pr_df.loc[i, 'mm21']
            volume_0 = pr_df.loc[i, 'vol']
            mv21_0 = pr_df.loc[i, 'mv21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                cond01_1 = close_1 / ma21_1 - 1 >= a and close_0 < ma21_0 and high_0 != close_0 and high_0 > ma21_0 and (
                    ma21_0 - close_0) / (high_0 - low_0) >= b and d >= volume_0 / mv21_0 - 1 >= e
                cond02_1 = close_1 / ma21_1 - 1 >= a and close_0 < ma21_0 and high_0 <= ma21_0 and close_0 / \
                    ma21_0 - 1 <= c and d >= volume_0 / mv21_0 - 1 >= e
                cond01 = cond01_1 or cond02_1
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bull_record = bull_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                         pr_df.loc[i, 'amt']]),
                        i, 'bull'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bull_record = bull_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                        i,
                        'bull'), ignore_index=True, sort=False)
        return bull_record
    elif action == 'BullOut':
        for data_i in range(len(sent_bull_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                ma21_0, ma21_1 = pr_df.loc[i,
                                           'ema21'], pr_df.loc[i - 1, 'ema21']
                close_0, close_1 = pr_df.loc[i,
                                             'close'], pr_df.loc[i - 1, 'close']
                low_0, high_0 = pr_df.loc[i, 'low'], pr_df.loc[i, 'high']
                volume_0 = pr_df.loc[i, 'vol']
                mv21_0 = pr_df.loc[i, 'mv21']
                cond01_1 = close_1 / ma21_1 - 1 >= a and close_0 < ma21_0 and high_0 != close_0 and high_0 > ma21_0 and (
                    ma21_0 - close_0) / (high_0 - low_0) >= b and d >= volume_0 / mv21_0 - 1 >= e
                cond02_1 = close_1 / ma21_1 - 1 >= a and close_0 < ma21_0 and high_0 <= ma21_0 and close_0 / \
                    ma21_0 - 1 <= c and d >= volume_0 / mv21_0 - 1 >= e
                cond01 = cond01_1 or cond02_1
                if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / sent_bull_record.loc[
                    data_i, 'buy_p'] - 1 >= BullTP or (
                        cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                    sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                  out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bull_record
    elif action == 'BearIn':
        for i in range(fst_idx, last_idx):
            ma21_0, ma21_1 = pr_df.loc[i, 'ema21'], pr_df.loc[i - 1, 'ema21']
            close_0, close_1 = pr_df.loc[i, 'close'], pr_df.loc[i - 1, 'close']
            low_0, high_0 = pr_df.loc[i, 'low'], pr_df.loc[i, 'high']
            mon_amt = pr_df.loc[i, 'mm21']
            volume_0 = pr_df.loc[i, 'vol']
            mv21_0 = pr_df.loc[i, 'mv21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                cond01_1 = close_1 / ma21_1 - 1 >= a and close_0 < ma21_0 and high_0 != close_0 and high_0 > ma21_0 and (
                    ma21_0 - close_0) / (high_0 - low_0) >= b and d >= volume_0 / mv21_0 - 1 >= e
                cond02_1 = close_1 / ma21_1 - 1 >= a and close_0 < ma21_0 and high_0 <= ma21_0 and close_0 / \
                    ma21_0 - 1 <= c and d >= volume_0 / mv21_0 - 1 >= e
                cond01 = cond01_1 or cond02_1
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bear_record = bear_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                         pr_df.loc[i, 'amt']]),
                        i, 'bear'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bear_record = bear_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                        i,
                        'bear'), ignore_index=True, sort=False)
        return bear_record
    else:
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                ma21_0, ma21_1 = pr_df.loc[i,
                                           'ema21'], pr_df.loc[i - 1, 'ema21']
                close_0, close_1 = pr_df.loc[i,
                                             'close'], pr_df.loc[i - 1, 'close']
                low_0, high_0 = pr_df.loc[i, 'low'], pr_df.loc[i, 'high']
                volume_0 = pr_df.loc[i, 'vol']
                mv21_0 = pr_df.loc[i, 'mv21']
                cond01_1 = close_1 / ma21_1 - 1 >= a and close_0 < ma21_0 and high_0 != close_0 and high_0 > ma21_0 and (
                    ma21_0 - close_0) / (high_0 - low_0) >= b and d >= volume_0 / mv21_0 - 1 >= e
                cond02_1 = close_1 / ma21_1 - 1 >= a and close_0 < ma21_0 and high_0 <= ma21_0 and close_0 / \
                    ma21_0 - 1 <= c and d >= volume_0 / mv21_0 - 1 >= e
                cond01 = cond01_1 or cond02_1
                if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / \
                        sent_bear_record.loc[
                        data_i, 'sell_p'] - 1 <= -BearTP or (
                        cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                    sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bear_record


def PriceChgAtHighLevel(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=-0.01, b=0.6, c=-0.01, d=1, e=-1, f=0.01, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('BullCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv('BearCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ExeTA(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_len, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if action == 'BearOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                close_0, high_0, low_0, open_0 = pr_df.loc[i, 'close'], pr_df.loc[i,
                                                                                  'high'], pr_df.loc[i, 'low'], pr_df.loc[i, 'open']
                closechg_89, mon_amt = close_0 / \
                    pr_df.loc[i - 89:i - 1]['close'].min() - \
                    1, pr_df.loc[i, 'mm21']
                high_bias_cnt = 0
                a = int(round(a, 0))
                if a < min_idx:
                    for j in range(i - a, i + 1):
                        bias_5ema = pr_df.loc[j, 'close'] / \
                            pr_df.loc[j, 'ema5'] - 1
                        if bias_5ema > b:
                            high_bias_cnt += 1
                upper_shadow = high_0 / close_0 - 1 if close_0 >= open_0 else high_0 / open_0 - 1
                lower_shadow = close_0 / low_0 - 1 if close_0 <= open_0 else open_0 / low_0 - 1
                real_body, amt_chg = open_0 / close_0 - \
                    1, pr_df.loc[i, 'amt'] / mon_amt - 1 if mon_amt > 0 else 0
                cond01 = closechg_89 >= d and (
                    upper_shadow >= e or lower_shadow >= e or real_body >= e) and amt_chg >= f and high_bias_cnt / (a + 1) >= c
                if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / sent_bear_record.loc[
                    data_i, 'sell_p'] - 1 <= -BearTP or (
                        cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                    sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bear_record
    elif action == 'BearIn':
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                close_0, high_0, low_0, open_0 = pr_df.loc[i, 'close'], pr_df.loc[i, 'high'], pr_df.loc[i, 'low'], \
                    pr_df.loc[i, 'open']
                closechg_89 = close_0 / \
                    pr_df.loc[i - 89:i - 1]['close'].min() - 1
                high_bias_cnt = 0
                a = int(round(a, 0))
                if a < min_idx:
                    for j in range(i - a, i + 1):
                        bias_5ema = pr_df.loc[j, 'close'] / \
                            pr_df.loc[j, 'ema5'] - 1
                        if bias_5ema > b:
                            high_bias_cnt += 1
                upper_shadow = high_0 / close_0 - 1 if close_0 >= open_0 else high_0 / open_0 - 1
                lower_shadow = close_0 / low_0 - 1 if close_0 <= open_0 else open_0 / low_0 - 1
                real_body, amt_chg = open_0 / close_0 - \
                    1, pr_df.loc[i, 'amt'] / mon_amt - 1 if mon_amt > 0 else 0
                cond01 = closechg_89 >= d and (
                    upper_shadow >= e or lower_shadow >= e or real_body >= e) and amt_chg >= f and high_bias_cnt / (a + 1) >= c
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bear_record = bear_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                         pr_df.loc[i, 'amt']]),
                        i, 'bear'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bear_record = bear_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                        i,
                        'bear'), ignore_index=True, sort=False)
        return bear_record
    elif action == 'BullOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                close_0, high_0, low_0, open_0 = pr_df.loc[i, 'close'], pr_df.loc[i, 'high'], pr_df.loc[i, 'low'], \
                    pr_df.loc[i, 'open']
                closechg_89, mon_amt = close_0 / \
                    pr_df.loc[i - 89:i - 1]['close'].min() - \
                    1, pr_df.loc[i, 'mm21']
                high_bias_cnt = 0
                a = int(round(a, 0))
                if a < min_idx:
                    for j in range(i - a, i + 1):
                        bias_5ema = pr_df.loc[j, 'close'] / \
                            pr_df.loc[j, 'ema5'] - 1
                        if bias_5ema > b:
                            high_bias_cnt += 1
                upper_shadow = high_0 / close_0 - 1 if close_0 >= open_0 else high_0 / open_0 - 1
                lower_shadow = close_0 / low_0 - 1 if close_0 <= open_0 else open_0 / low_0 - 1
                real_body, amt_chg = open_0 / close_0 - \
                    1, pr_df.loc[i, 'amt'] / mon_amt - 1 if mon_amt > 0 else 0
                cond01 = closechg_89 >= d and (
                    upper_shadow >= e or lower_shadow >= e or real_body >= e) and amt_chg >= f and high_bias_cnt / (a + 1) >= c
                if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / sent_bull_record.loc[
                    data_i, 'buy_p'] - 1 >= BullTP or (
                        cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                    sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                  out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bull_record
    else:
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                close_0, high_0, low_0, open_0 = pr_df.loc[i, 'close'], pr_df.loc[i, 'high'], pr_df.loc[i, 'low'], \
                    pr_df.loc[i, 'open']
                closechg_89 = close_0 / \
                    pr_df.loc[i - 89:i - 1]['close'].min() - 1
                high_bias_cnt = 0
                a = int(round(a, 0))
                if a < min_idx:
                    for j in range(i - a, i + 1):
                        bias_5ema = pr_df.loc[j, 'close'] / \
                            pr_df.loc[j, 'ema5'] - 1
                        if bias_5ema > b:
                            high_bias_cnt += 1
                upper_shadow = high_0 / close_0 - 1 if close_0 >= open_0 else high_0 / open_0 - 1
                lower_shadow = close_0 / low_0 - 1 if close_0 <= open_0 else open_0 / low_0 - 1
                real_body, amt_chg = open_0 / close_0 - \
                    1, pr_df.loc[i, 'amt'] / mon_amt - 1 if mon_amt > 0 else 0
                cond01 = closechg_89 >= d and (
                    upper_shadow >= e or lower_shadow >= e or real_body >= e) and amt_chg >= f and high_bias_cnt / (a + 1) >= c
                if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                    bull_record = bull_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                         pr_df.loc[i, 'amt']]),
                        i, 'bull'), ignore_index=True, sort=False)
                elif cond01 and mode == 'select':
                    bull_record = bull_record.append(CalFeature(pr_df, np.array(
                        [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                        i,
                        'bull'), ignore_index=True, sort=False)
        return bull_record


def FallBelowHighPressure(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=5, b=0.02, c=1, d=1.5, e=0.025, f=0.05, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('BullCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv('BearCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ExeTA(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_len, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if action == 'BearOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                close_0, low_0, cond01 = pr_df.loc[i,
                                                   'close'], pr_df.loc[i, 'low'], False
                closechg_89 = close_0 / \
                    pr_df.loc[i - 89:i - 1]['close'].min() - 1
                if closechg_89 >= c and close_0 == low_0 and pr_df.loc[i - 1, 'close'] / close_0 - 1 >= e:
                    a = int(round(a, 0))
                    if a < max_len:
                        for j in range(i - a, i - 1):
                            close_a, vol_a, low_a, high_a = pr_df.loc[j, 'close'], pr_df.loc[
                                j, 'vol'], pr_df.loc[j, 'low'], pr_df.loc[j, 'high']
                            if low_a / close_0 - 1 >= b and low_a == close_a and vol_a >= d * pr_df.loc[j, 'mv21'] and high_a / low_a - 1 >= f:
                                cond01 = True
                                break
                if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / sent_bear_record.loc[
                    data_i, 'sell_p'] - 1 <= -BearTP or (
                        cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                    sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bear_record
    elif action == 'BearIn':
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                close_0, low_0, cond01 = pr_df.loc[i,
                                                   'close'], pr_df.loc[i, 'low'], False
                closechg_89 = close_0 / \
                    pr_df.loc[i - 89:i - 1]['close'].min() - 1
                if closechg_89 >= c and close_0 == low_0 and pr_df.loc[i - 1, 'close'] / close_0 - 1 >= e:
                    a = int(round(a, 0))
                    if a < max_len:
                        for j in range(i - a, i - 1):
                            close_a, vol_a, low_a, high_a = pr_df.loc[j, 'close'], pr_df.loc[j,
                                                                                             'vol'], pr_df.loc[j, 'low'], pr_df.loc[j, 'high']
                            if low_a / close_0 - 1 >= b and low_a == close_a and vol_a >= d * pr_df.loc[i - a, 'mv21'] and high_a / low_a - 1 >= f:
                                cond01 = True
                                break
                    if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                        bear_record = bear_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                             pr_df.loc[i, 'amt']]), i, 'bear'), ignore_index=True, sort=False)
                    elif cond01 and mode == 'select':
                        bear_record = bear_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                            i,
                            'bear'), ignore_index=True, sort=False)
        return bear_record
    elif action == 'BullOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                close_0, low_0, cond01 = pr_df.loc[i,
                                                   'close'], pr_df.loc[i, 'low'], False
                closechg_89 = close_0 / \
                    pr_df.loc[i - 89:i - 1]['close'].min() - 1
                if closechg_89 >= c and close_0 == low_0 and pr_df.loc[i - 1, 'close'] / close_0 - 1 >= e:
                    a = int(round(a, 0))
                    if a < max_len:
                        for j in range(i - a, i - 1):
                            close_a, vol_a, low_a, high_a = pr_df.loc[j, 'close'], pr_df.loc[
                                j, 'vol'], pr_df.loc[j, 'low'], pr_df.loc[j, 'high']
                            if low_a / close_0 - 1 >= b and low_a == close_a and vol_a >= d * pr_df.loc[j, 'mv21'] and high_a / low_a - 1 >= f:
                                cond01 = True
                                break
                if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / sent_bull_record.loc[
                    data_i, 'buy_p'] - 1 >= BullTP or (
                        cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                    sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                  out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bull_record
    else:
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'mm21']
            if mon_amt >= MonAmt and pr_df.loc[i, 'amt'] >= MonAmt:
                close_0, low_0, cond01 = pr_df.loc[i,
                                                   'close'], pr_df.loc[i, 'low'], False
                closechg_89 = close_0 / \
                    pr_df.loc[i - 89:i - 1]['close'].min() - 1
                if closechg_89 >= c and close_0 == low_0 and pr_df.loc[i - 1, 'close'] / close_0 - 1 >= e:
                    a = int(round(a, 0))
                    if a < max_len:
                        for j in range(i - a, i - 1):
                            close_a, vol_a, low_a, high_a = pr_df.loc[j, 'close'], pr_df.loc[j,
                                                                                             'vol'], pr_df.loc[j, 'low'], pr_df.loc[j, 'high']
                            if low_a / close_0 - 1 >= b and low_a == close_a and vol_a >= d * pr_df.loc[i - a, 'mv21'] and high_a / low_a - 1 >= f:
                                cond01 = True
                                break
                    if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                        bull_record = bull_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                             pr_df.loc[i, 'amt']]),
                            i, 'bull'), ignore_index=True, sort=False)
                    elif cond01 and mode == 'select':
                        bull_record = bull_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                            i,
                            'bull'), ignore_index=True, sort=False)
        return bull_record


def HMADecline(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=9, b=16, c=0, d=0.45, e=0.1, f=9, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('BullCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv('BearCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ToWeekKBar(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_wk, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if int(a) == int(b):
        key_tup = (9, 16)
        print('modified parameter:', a, b)
    else:
        key_tup = (int(a), int(b))
    hma_tup, f = ('hma' + str(a), 'hma' + str(b)
                  ), 17 if int(f) > 17 else int(f)
    for num, n in enumerate(key_tup):
        half_n, root_n = int(round(n / 2, 0)), int(round(pow(n, 0.5), 0))
        c_copy = pd.DataFrame({'close': []})
        hma_1 = 2 * abstract.WMA(pr_df, half_n)
        hma_2 = abstract.WMA(pr_df, n)
        c_copy['close'] = hma_1 - hma_2
        pr_df[hma_tup[num]] = abstract.WMA(c_copy, root_n)
    if action == 'BearOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                close_0, cond01 = pr_df.loc[i, 'close'], False
                pass_df = pr_df.loc[i - f:i]['close']
                high_chg = np.log(pass_df.max() / close_0)
                low_chg = np.log(close_0 / pass_df.min())
                if c <= high_chg <= d and e <= low_chg:
                    for hma in hma_tup:
                        if pr_df.loc[i - 1, hma] > max(pr_df.loc[i, hma], pr_df.loc[i - 2, hma]):
                            cond01 = True
                            break
                if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / sent_bear_record.loc[
                    data_i, 'sell_p'] - 1 <= -BearTP or (
                        cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                    sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bear_record
    elif action == 'BearIn':
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'max4amt']
            if mon_amt >= MonAmt * 5 and pr_df.loc[i, 'amt'] >= MonAmt * 5:
                close_0, cond01 = pr_df.loc[i, 'close'], False
                pass_df = pr_df.loc[i - f:i]['close']
                high_chg = np.log(pass_df.max() / close_0)
                low_chg = np.log(close_0 / pass_df.min())
                if c <= high_chg <= d and e <= low_chg:
                    for hma in hma_tup:
                        if pr_df.loc[i - 1, hma] > max(pr_df.loc[i, hma], pr_df.loc[i - 2, hma]):
                            cond01 = True
                            break
                    if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                        bear_record = bear_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                             pr_df.loc[i, 'amt']]), i, 'bear'), ignore_index=True, sort=False)
                    elif cond01 and mode == 'select':
                        bear_record = bear_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                            i,
                            'bear'), ignore_index=True, sort=False)
        return bear_record
    elif action == 'BullOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                close_0, cond01 = pr_df.loc[i, 'close'], False
                pass_df = pr_df.loc[i - f:i]['close']
                high_chg = np.log(pass_df.max() / close_0)
                low_chg = np.log(close_0 / pass_df.min())
                if c <= high_chg <= d and e <= low_chg:
                    for hma in hma_tup:
                        if pr_df.loc[i - 1, hma] > max(pr_df.loc[i, hma], pr_df.loc[i - 2, hma]):
                            cond01 = True
                            break
                if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / sent_bull_record.loc[
                    data_i, 'buy_p'] - 1 >= BullTP or (
                        cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                    sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                  out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bull_record
    else:
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'max4amt']
            if mon_amt >= MonAmt * 5 and pr_df.loc[i, 'amt'] >= MonAmt * 5:
                close_0, cond01 = pr_df.loc[i, 'close'], False
                pass_df = pr_df.loc[i - f:i]['close']
                high_chg = np.log(pass_df.max() / close_0)
                low_chg = np.log(close_0 / pass_df.min())
                if c <= high_chg <= d and e <= low_chg:
                    for hma in hma_tup:
                        if pr_df.loc[i - 1, hma] > max(pr_df.loc[i, hma], pr_df.loc[i - 2, hma]):
                            cond01 = True
                            break
                    if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                        bull_record = bull_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                             pr_df.loc[i, 'amt']]),
                            i, 'bull'), ignore_index=True, sort=False)
                    elif cond01 and mode == 'select':
                        bull_record = bull_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                            i,
                            'bull'), ignore_index=True, sort=False)
        return bull_record


def HMARise(code, action, BullSL, BullTP, BearSL, BearTP, sent_bull_record, sent_bear_record, a=9, b=16, c=0, d=0.45, e=0.1, f=9, MonAmt=50000, mincp=0.03, mode='backtest'):
    bull_record, bear_record = pd.read_csv('BullCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'}), pd.read_csv('BearCol.csv').astype(
        {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    pr_df = ToWeekKBar(code, mode)
    fst_idx, last_idx = pr_df.head(1).index.to_list(
    )[0] + max_wk, pr_df.tail(1).index.to_list()[0] + mode_dict[mode]
    if int(a) == int(b):
        key_tup = (9, 16)
        print('modified parameter:', a, b)
    else:
        key_tup = (int(a), int(b))
    hma_tup, f = ('hma' + str(a), 'hma' + str(b)
                  ), 17 if int(f) > 17 else int(f)
    for num, n in enumerate(key_tup):
        half_n, root_n = int(round(n / 2, 0)), int(round(pow(n, 0.5), 0))
        c_copy = pd.DataFrame({'close': []})
        hma_1 = 2 * abstract.WMA(pr_df, half_n)
        hma_2 = abstract.WMA(pr_df, n)
        c_copy['close'] = hma_1 - hma_2
        pr_df[hma_tup[num]] = abstract.WMA(c_copy, root_n)
    if action == 'BearOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bear_record.loc[data_i, 'sell_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                close_0, cond01 = pr_df.loc[i, 'close'], False
                pass_df = pr_df.loc[i - f:i]['close']
                high_chg = np.log(pass_df.max() / close_0)
                low_chg = np.log(close_0 / pass_df.min())
                if c <= high_chg and d <= low_chg <= e:
                    for hma in hma_tup:
                        if pr_df.loc[i - 1, hma] < min(pr_df.loc[i, hma], pr_df.loc[i - 2, hma]):
                            cond01 = True
                            break
                if close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 >= BearSL or close_0 / sent_bear_record.loc[
                    data_i, 'sell_p'] - 1 <= -BearTP or (
                        cond01 and close_0 / sent_bear_record.loc[data_i, 'sell_p'] - 1 <= -mincp):
                    sent_bear_record.loc[data_i, 'buy_date'], sent_bear_record.loc[data_i, 'buy_p'] = pr_df.loc[i +
                                                                                                                out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bear_record
    elif action == 'BearIn':
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'max4amt']
            if mon_amt >= MonAmt * 5 and pr_df.loc[i, 'amt'] >= MonAmt * 5:
                close_0, cond01 = pr_df.loc[i, 'close'], False
                pass_df = pr_df.loc[i - f:i]['close']
                high_chg = np.log(pass_df.max() / close_0)
                low_chg = np.log(close_0 / pass_df.min())
                if c <= high_chg and d <= low_chg <= e:
                    for hma in hma_tup:
                        if pr_df.loc[i - 1, hma] < min(pr_df.loc[i, hma], pr_df.loc[i - 2, hma]):
                            cond01 = True
                            break
                    if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                        bear_record = bear_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                             pr_df.loc[i, 'amt']]), i, 'bear'), ignore_index=True, sort=False)
                    elif cond01 and mode == 'select':
                        bear_record = bear_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                            i,
                            'bear'), ignore_index=True, sort=False)
        return bear_record
    elif action == 'BullOut':
        for data_i in range(len(sent_bear_record)):
            start_idx = pr_df[pr_df['date'] == sent_bull_record.loc[data_i, 'buy_date']].index.to_list()[
                0]
            for i in range(start_idx + 1, last_idx):
                close_0, cond01 = pr_df.loc[i, 'close'], False
                pass_df = pr_df.loc[i - f:i]['close']
                high_chg = np.log(pass_df.max() / close_0)
                low_chg = np.log(close_0 / pass_df.min())
                if c <= high_chg and d <= low_chg <= e:
                    for hma in hma_tup:
                        if pr_df.loc[i - 1, hma] < min(pr_df.loc[i, hma], pr_df.loc[i - 2, hma]):
                            cond01 = True
                            break
                if close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 <= -BullSL or close_0 / sent_bull_record.loc[
                    data_i, 'buy_p'] - 1 >= BullTP or (
                        cond01 and close_0 / sent_bull_record.loc[data_i, 'buy_p'] - 1 >= mincp):
                    sent_bull_record.loc[data_i, 'sell_date'], sent_bull_record.loc[data_i, 'sell_p'] = pr_df.loc[i +
                                                                                                                  out_mode[mode][0], 'date'], pr_df.loc[i + out_mode[mode][0], out_mode[mode][1]]
                    break
        return sent_bull_record
    else:
        for i in range(fst_idx, last_idx):
            mon_amt = pr_df.loc[i, 'max4amt']
            if mon_amt >= MonAmt * 5 and pr_df.loc[i, 'amt'] >= MonAmt * 5:
                close_0, cond01 = pr_df.loc[i, 'close'], False
                pass_df = pr_df.loc[i - f:i]['close']
                high_chg = np.log(pass_df.max() / close_0)
                low_chg = np.log(close_0 / pass_df.min())
                if c <= high_chg and d <= low_chg <= e:
                    for hma in hma_tup:
                        if pr_df.loc[i - 1, hma] < min(pr_df.loc[i, hma], pr_df.loc[i - 2, hma]):
                            cond01 = True
                            break
                    if cond01 and mode == 'backtest' and pr_df.loc[i + 1, 'vol'] > 0:
                        bull_record = bull_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i + 1, 'date'], float(pr_df.loc[i + 1, 'open']), end, 0,
                             pr_df.loc[i, 'amt']]),
                            i, 'bull'), ignore_index=True, sort=False)
                    elif cond01 and mode == 'select':
                        bull_record = bull_record.append(CalFeature(pr_df, np.array(
                            [int(code), pr_df.loc[i, 'date'], float(pr_df.loc[i, 'close']), end, 0, pr_df.loc[i, 'amt']]),
                            i,
                            'bull'), ignore_index=True, sort=False)
        return bull_record


opt_dict = {'無': NoTrade, 'MACD綠柱收斂': MacdNegHistConverge, '突破均線糾結1': CrossOverTangledMA, '股價觸及箱頂': ReachTop, '突破均線糾結2': BreakThroughTangledMA, '股價跌破月線': FallBelow21EMA,
            '股價高檔反轉': PriceChgAtHighLevel, '股價跌破黑K低點': FallBelowHighPressure, 'HMA下彎': HMADecline, 'HMA上揚': HMARise}
