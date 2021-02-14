import pandas as pd
import numpy as np


def OptimalizeHMA():
    df1 = pd.read_csv(r"D:\2016_2019\analysis\HMA\hma9b.csv")
    df2 = pd.read_csv(r"D:\2016_2019\analysis\HMA\hma16b.csv")
    df_tup = (df1, df2)
    hma_tup = ('9', '16')
    for enum, df in enumerate(df_tup):
        df = df.astype({'code': 'int16'})
        test = ['hma5', 'hma4', 'hma3', 'hma2', 'hma1', 'hma0']
        cond_taiex = df['code'] == 1000
        cond_stocks = df['code'] > 1000
        group_tup = (cond_taiex, cond_stocks)
        name_tup = ('D:/2016_2019/analysis/HMA/taiex_singleHMA' +
                    hma_tup[enum] + '.csv', 'D:/2016_2019/analysis/HMA/stocks_singleHMA' + hma_tup[enum] + '.csv')
        for gr_i, group in enumerate(group_tup):
            stat = {'odds': [], 'glr': [], 'appt': [], 'num': [], 'ratio': [], 'chg_amt_med': [], 'hma5_max': [],
                    'hma5_min': [], 'hma4_max': [], 'hma4_min': [], 'hma3_max': [], 'hma3_min': [], 'hma2_max': [], 'hma2_min': [], 'hma1_max': [], 'hma1_min': [], 'hma0_max': [], 'hma0_min': []}
            for seq, ele in enumerate(test):
                maxval = round(df[group][ele].max(), 5)
                minval = round(df[group][ele].min(), 5)
                print(ele)
                for hma_max in np.arange(maxval, minval, -0.01):
                    for hma_min in np.arange(minval, maxval, 0.01):
                        cond01_1 = df[ele] < hma_max
                        cond01_2 = hma_min < df[ele]
                        cond01 = cond01_1 & cond01_2 & group
                        win_df = df[cond01]['win']
                        len_win = len(win_df)
                        if len_win > 0:
                            num, ratio = len_win, len_win / len(df[group])
                            cond02 = df['chg_amt'] > 0
                            cond03 = df['chg_amt'] <= 0
                            gdf, ldf = df[cond01 &
                                          cond02]['chg_amt'], df[cond01 & cond03]['chg_amt']
                            print(len_win, 100 * len_win / len(df))
                            odds = win_df.sum() / len_win
                            if len(gdf) != 0 and len(ldf) != 0:
                                gain, loss = gdf.sum() / len(gdf), ldf.sum() / len(ldf)
                                glr = abs(gain / loss)
                                appt = gain * odds + loss * (1 - odds)
                            elif len(gdf) != 0 and len(ldf) == 0:
                                gain = gdf.sum() / len(gdf)
                                appt, glr = gain, np.NaN
                            elif len(gdf) == 0 and len(ldf) != 0:
                                loss = ldf.sum() / len(ldf)
                                appt, glr = loss, 0
                            else:
                                raise ValueError
                            chg_amt_med = df[cond01]['chg_amt'].median()
                            stat['odds'].append(odds)
                            stat['glr'].append(glr)
                            stat['appt'].append(appt)
                            stat['num'].append(num)
                            stat['ratio'].append(ratio)
                            stat['chg_amt_med'].append(chg_amt_med)
                            stat[ele + '_max'].append(hma_max)
                            stat[ele + '_min'].append(hma_min)
                            if seq < 5:
                                redundant = test[seq - 5:] + test[:seq]
                            else:
                                redundant = test[:seq]
                            for item in redundant:
                                stat[item + '_max'].append(np.NaN)
                                stat[item + '_min'].append(np.NaN)
                        else:
                            print('length = 0', hma_max, hma_min, ele)
            pd.DataFrame(stat).to_csv(name_tup[gr_i])
            print('done', name_tup[gr_i])
