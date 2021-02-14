# coding=utf-8
import time
import json
import requests
import random
from matplotlib import ticker
import tkinter.font as tkfont
import matplotlib.lines as mlines
from pandas.plotting import register_matplotlib_converters
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib
from cmath import exp, log
from StkTrade import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
from decimal import Decimal
from datetime import datetime
from mplfinance.original_flavor import candlestick_ohlc
from PIL import Image, ImageTk
from scipy import stats
from os import listdir
import traceback
from os import path
from bs4 import BeautifulSoup as BS
matplotlib.use('TkAgg')
register_matplotlib_converters()
date_lt, code_lt, name_lt = [], [], []
strategy_lt, pct_lt, select_dict = list(opt_dict.keys()), [2.5, 5, 7.5, 10, 12.5], {
    '成交量(仟元)': 'amt', 'DI+': 'DI+', 'DI-': 'DI-', 'K值': 'slowk13', 'D值': 'slowd13', '布林帶寬': 'bandwidth', '布林帶寬變化率': 'bandchg'}
reverse_select, not_percent = {v: k for k, v in select_dict.items()}, [
    'amt', 'DI+', 'DI-', 'slowk13', 'slowd13']
capital_df = pd.read_csv(r"D:\2016_2019\capital.csv")
bull_col_lt, bear_col_lt = bull_columns, bear_columns
datetime_str = datetime.now().strftime('%Y%m%d%H%M')
time_now = datetime_str[2:]
fut_path = r"D:\2016_2019\taifex"
fee, tax, margin, mkt_ret, int_year_now, int_year_ini = 0.000855, 0.003, 0.9, 0, int(
    datetime_str[:4]), int(min_date.strftime('%Y'))
color_lt = ['#12c6e6', '#008B8B', '#FF69B4', '#00FA9A', '#CCBBFF',
            '#EE7700', '#C4AA00', '#026a9e', '#b32557', '#FFC0CB', '#B8860B']
heading_lt = ['總交易次數', '獲利次數', '虧損次數',
              '勝率%', '單筆最高報酬率%', '單筆最低報酬率%', '年化報酬率%',
              '單日最大獲利率%', '最大回撤%', '單日最大虧損率%', '最大連續獲利率%',
                          '最大連續虧損率%', '單筆最高幾何報酬率%', '單筆最低幾何報酬率%', '總報酬率%',
                          '平均報酬率%', 'Sortino ratio', 'cnt_dict', 'win_cnt_dict', 'loss_cnt_dict', '賺賠比', 'alpha', 'beta']
with open('D:/stocks/tdy.txt', newline='\n', encoding='utf-8') as tf:
    tdy = list(csv.reader(tf))[-1][0]
datetime_tdy = pd.to_datetime(tdy, format='%Y%m%d')
with open('D:/stocks/filter.txt', newline='\n', encoding='utf-8') as code_f:
    reader = list(csv.reader(code_f))
    for r in reader:
        code_lt.append(r[0])
        name_lt.append(r[1])
ret_df = pd.read_csv('D:/2016_2019/cp/ret_cp.csv', parse_dates=['date'])
hd = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}


def getIndex(date, num):
    url = 'https://www.twse.com.tw/exchangeReport/FMTQIK?response=json&date=' + date
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'data' in jdata and 'fields' in jdata:
            all_data = jdata['data']
            field = jdata['fields']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['taiex_close網址的key已改變', datetime.now()])
                print('Website_of_taiex_close_has_changed')
            raise ValueError
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getIndex(date, num)
        else:
            raise err
    else:
        if field == ["日期", "成交股數", "成交金額", "成交筆數", "發行量加權股價指數", "漲跌點數"] and len(all_data) != 0:
            with open(r"D:\2016_2019\TAIEX\taiex_close.csv", newline='\n', encoding='utf-8') as cr:
                chk = [row[0] for row in csv.reader(cr)]
            all_input_data = []
            for line in all_data:
                split_lt = line[0].split('/')
                date_str = str(int(split_lt[0]) +
                               1911) + split_lt[1] + split_lt[2]
                if date_str not in chk:
                    all_input_data.append(
                        [date_str, line[1].replace(',', ''), line[2].replace(',', ''), line[3].replace(',', ''),
                         line[4].replace(',', ''), line[5].replace(',', '')])
            done_date_lt = []
            with open(r"D:\2016_2019\TAIEX\taiex_close.csv", 'a', newline='\n', encoding='utf-8') as cr:
                wr = csv.writer(cr)
                for line in all_input_data:
                    wr.writerow(line)
                    done_date_lt.append(line[0])
            with open('D:/stocks/taiex_close_done.txt', 'a', newline='\n', encoding='utf-8') as prd:
                if done_date_lt != []:
                    wr = csv.writer(prd)
                    for done_date in done_date_lt:
                        wr.writerow([done_date])
                        print('Done taiex close', done_date)
                else:
                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as nf:
                        wr = csv.writer(nf)
                        wr.writerow(
                            ['今日未新增加權指數', date, datetime.now(), 'all input data如下:'])
                        for line in all_input_data:
                            wr.writerow(line)
                            print('No taiex close', line[0])
        elif field != ["日期", "成交股數", "成交金額", "成交筆數", "發行量加權股價指數", "漲跌點數"] and len(all_data) != 0:
            with open('D:/stocks/No_Index.txt', 'a', newline='\n', encoding='utf-8') as nf:
                wr = csv.writer(nf)
                wr.writerow(['欄位改變', date, datetime.now()])
        else:
            with open('D:/stocks/No_Index.txt', 'a', newline='\n', encoding='utf-8') as nf:
                wr = csv.writer(nf)
                wr.writerow(['沒資料', date, datetime.now()])


def getOHLC(date, num):
    url = 'https://www.twse.com.tw/indicesReport/MI_5MINS_HIST?response=json&date=' + \
        str(date)
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'data' in jdata and 'fields' in jdata:
            all_data = jdata['data']
            field = jdata['fields']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['taiexOHLC的key已改變', datetime.now()])
                print('Website_of_taiexOHLC_has_changed')
            raise ValueError
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getOHLC(date, num)
        else:
            raise err
    else:
        if field == ["日期", "開盤指數", "最高指數", "最低指數", "收盤指數"] and len(all_data) != 0:
            with open(r"D:\2016_2019\TAIEX\taiex.csv", newline='\n', encoding='utf-8') as cr:
                chk = [row[0] for row in csv.reader(cr)]
            all_input_data = []
            for line in all_data:
                split_lt = line[0].split('/')
                date_str = str(int(split_lt[0]) +
                               1911) + split_lt[1] + split_lt[2]
                if date_str not in chk:
                    all_input_data.append([date_str, line[1].replace(',', ''), line[2].replace(
                        ',', ''), line[3].replace(',', ''), line[4].replace(',', '')])
            taiex_close_df = pd.read_csv(
                r"D:\2016_2019\TAIEX\taiex_close.csv", parse_dates=['date'])
            done_date_lt, concat_dict = [], {
                'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'vol': []}
            key_tup = tuple(concat_dict.keys())
            ptaiex = pd.read_csv('D:/2016_2019/p/p1000.csv')
            with open(r"D:\2016_2019\TAIEX\taiex.csv", 'a', newline='\n', encoding='utf-8') as cr:
                wr = csv.writer(cr)
                for row in all_input_data:
                    idx_lt = taiex_close_df[taiex_close_df['date'] == pd.to_datetime(
                        row[0], format='%Y%m%d')].index.to_list()
                    if len(idx_lt) != 0:
                        data_idx = idx_lt[0]
                        tdy_amt = taiex_close_df.loc[data_idx,
                                                     'amt'] / 100000000
                        new_row = row + [tdy_amt]
                        wr.writerow(new_row)
                        for enum, row_ele in enumerate(new_row):
                            concat_dict[key_tup[enum]].append(row_ele)
                        done_date_lt.append(row[0])
                    else:
                        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                            wr = csv.writer(erf)
                            wr.writerow(
                                ['無法在taiex close找到' + row[0] + ' 的成交量資訊'])
            if concat_dict['date'] != []:
                concat_df = pd.DataFrame(concat_dict)
                new_df = pd.concat([ptaiex, concat_df],
                                   ignore_index=True, sort=False)
                new_df.to_csv('D:/2016_2019/p/p1000.csv', index=False)
            else:
                print('p1000.csv 未新增資料')
            with open('D:/stocks/taiex_OHLC_done.txt', 'a', newline='\n', encoding='utf-8') as prd:
                if done_date_lt != []:
                    wr = csv.writer(prd)
                    for done_date in done_date_lt:
                        wr.writerow([done_date])
                        print('Done taiex OHLC', done_date)
                else:
                    with open('No_Index.txt', 'a', newline='\n', encoding='utf-8') as nf:
                        wr = csv.writer(nf)
                        wr.writerow(
                            ['沒 taiex OHLC 的資料', date, datetime.now(), 'all input data如下:'])
                        for line in all_input_data:
                            wr.writerow(line)
                            print('No taiex OHLC', line[0])
        elif field != ["日期", "開盤指數", "最高指數", "最低指數", "收盤指數"] and len(all_data) != 0:
            with open('D:/stocks/No_Index.txt', 'a', newline='\n', encoding='utf-8') as nf:
                wr = csv.writer(nf)
                wr.writerow(['OHLC欄位改變', datetime.now()])
        else:
            with open('D:/stocks/No_Index.txt', 'a', newline='\n', encoding='utf-8') as nf:
                wr = csv.writer(nf)
                wr.writerow(['沒OHLC資料', datetime.now()])


def getRetIndex(date, num):
    url = 'https://www.twse.com.tw/indicesReport/MFI94U?response=json&date=' + date
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'data' in jdata and 'fields' in jdata:
            all_data = jdata['data']
            field = jdata['fields']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['報酬指數網址的key已改變', datetime.now()])
                print('Website_of_daily_return_has_changed')
            raise ValueError
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getRetIndex(date, num)
        else:
            raise err
    else:
        if len(all_data) != 0:
            if len(field) != 2:
                with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as nf:
                    wr = csv.writer(nf)
                    wr.writerow(['報酬指數欄位改變', date, datetime.now()])
            with open(r"D:\2016_2019\TAIEX\ret.csv", newline='\n', encoding='utf-8') as cr:
                chk = [row[0] for row in csv.reader(cr)]
            with open(r"D:\2016_2019\cp\ret_cp.csv", newline='\n', encoding='utf-8') as retcp:
                ret_rd = list(csv.reader(retcp))
                ini = float(ret_rd[1][1])
            all_input_data = []
            for line in all_data:
                split_lt = line[0].split('/')
                date_str = str(int(split_lt[0]) +
                               1911) + split_lt[1] + split_lt[2]
                if date_str not in chk:
                    all_input_data.append(
                        [date_str, line[1].replace(',', '')])
            done_date_lt = []
            for line in all_input_data:
                with open(r"D:\2016_2019\TAIEX\ret.csv", 'a', newline='\n', encoding='utf-8') as cr:
                    wr = csv.writer(cr)
                    wr.writerow(line)
                with open(r"D:\2016_2019\cp\ret_cp.csv", 'a', newline='\n', encoding='utf-8') as retcp:
                    wr = csv.writer(retcp)
                    wr.writerow([line[0], line[1], float(line[1]) / ini - 1])
                done_date_lt.append(line[0])
            with open('D:/stocks/ret_done.txt', 'a', newline='\n', encoding='utf-8') as prd:
                if done_date_lt != []:
                    wr = csv.writer(prd)
                    for done_date in done_date_lt:
                        wr.writerow([done_date])
                        print('Done ret', done_date)
                else:
                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as nf:
                        wr = csv.writer(nf)
                        wr.writerow(
                            ['今日未新增報酬指數', date, datetime.now(), 'all input data如下:'])
                        for line in all_input_data:
                            wr.writerow(line)
                            print('No ret', line[0])
        else:
            with open('D:/stocks/No_Index.txt', 'a', newline='\n', encoding='utf-8') as nf:
                wr = csv.writer(nf)
                wr.writerow(['沒報酬指數的資料', date, datetime.now()])


def getCapRed(num):
    url = 'https://www.twse.com.tw/exchangeReport/TWTAVU?response=json'
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'data' in jdata:
            all_data = jdata['data']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['減資網址的key已改變', datetime.now()])
                print('Website_of_CapRed_has_changed')
            return 0
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getCapRed(num)
        else:
            raise err
    else:
        for Data in all_data:
            data_lt = []
            for i in range(9):
                data_lt.append(Data[i])
            with open(r"D:\2016_2019\msg\CapRed.txt", newline='\n', encoding='utf-8') as cr:
                chk = list(csv.reader(cr))
            if data_lt[1] in code_lt and data_lt not in chk:
                with open(r"D:\2016_2019\msg\CapRed.txt", 'a', newline='\n', encoding='utf-8') as cr:
                    wr = csv.writer(cr)
                    wr.writerow(data_lt)
                print('Done_CapRed')
            else:
                print('CapRed_existed')


def getDiv(num):
    url = 'https://www.twse.com.tw/exchangeReport/TWT48U?response=json'
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'data' in jdata:
            all_data = jdata['data']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['除權息網址的key已改變', datetime.now()])
                print('Website_of_dividend_has_changed')
            return 0
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getCapRed(num)
        else:
            raise err
    else:
        for Data in all_data:
            data_lt = []
            for i in range(11):
                if i == 10:
                    soup = BS(Data[i], 'lxml')
                    date_str = soup.select_one('a').text
                    data_lt.append(date_str)
                elif i != 8 and i != 9:
                    data_lt.append(Data[i])
            with open(r"D:\2016_2019\msg\Dividend.txt", newline='\n', encoding='utf-8') as cr:
                chk = list(csv.reader(cr))
            if data_lt[0] in code_lt and data_lt not in chk:
                with open(r"D:\2016_2019\msg\Dividend.txt", 'a', newline='\n', encoding='utf-8') as cr:
                    wr = csv.writer(cr)
                    wr.writerow(data_lt)
                print('Done_Dividend')
            else:
                print('Data_existed')


def getStopMar(num):
    url = 'https://www.twse.com.tw/exchangeReport/BFI84U?response=json'
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'data' in jdata:
            all_data = jdata['data']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['減資網址的key已改變', datetime.now()])
                print('Website_of_decap_has_changed')
            return 0
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getCapRed(num)
        else:
            raise err
    else:
        for Data in all_data:
            if Data[0] in code_lt:
                data_lt = []
                for i in range(5):
                    data_lt.append(Data[i])
                with open(r"D:\2016_2019\msg\StopMar.txt", newline='\n', encoding='utf-8') as cr:
                    chk = list(csv.reader(cr))
                if data_lt not in chk:
                    with open(r"D:\2016_2019\msg\StopMar.txt", 'a', newline='\n', encoding='utf-8') as cr:
                        wr = csv.writer(cr)
                        wr.writerow(data_lt)
                    print('Done_StopMar')
                else:
                    print('Data_existed.')


def getOtcMar(num):
    url = 'https://www.tpex.org.tw/web/stock/margin_trading/term/term_result.php?l=zh-tw'
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'aaData' in jdata:
            all_data = jdata['aaData']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['otc停券網址的key已改變', datetime.now()])
                print('Website_of_OtcStopMar_has_changed.')
            return 0
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getCapRed(num)
        else:
            raise err
    else:
        for Data in all_data:
            if Data[0] in code_lt:
                data_lt = []
                for i in Data:
                    data_lt.append(i)
                with open(r"D:\2016_2019\msg\Otc_StopMar.txt", newline='\n', encoding='utf-8') as cr:
                    chk = list(csv.reader(cr))
                if data_lt not in chk:
                    with open(r"D:\2016_2019\msg\Otc_StopMar.txt", 'a', newline='\n', encoding='utf-8') as cr:
                        wr = csv.writer(cr)
                        wr.writerow(data_lt)
                    print('Done_OtcStopMar')
                else:
                    print('Data_existed.')


def getOtcDiv(num):
    url = 'https://www.tpex.org.tw/web/stock/exright/preAnnounce/PrePost_result.php?l=zh-tw'
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'aaData' in jdata:
            all_data = jdata['aaData']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['otc除權息網址的key已改變', datetime.now()])
                print('Website_of_otc_dividend_has_changed.')
            return 0
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getCapRed(num)
        else:
            raise err
    else:
        for Data in all_data:
            if Data[1] in code_lt:
                data_lt = []
                for i in range(len(Data) - 1):
                    data_lt.append(Data[i])
                with open(r"D:\2016_2019\msg\OtcDiv.txt", newline='\n', encoding='utf-8') as cr:
                    chk = list(csv.reader(cr))
                if data_lt not in chk:
                    with open(r"D:\2016_2019\msg\OtcDiv.txt", 'a', newline='\n', encoding='utf-8') as cr:
                        wr = csv.writer(cr)
                        wr.writerow(data_lt)
                    print('Done_OtcDiv')
                else:
                    print('Data_existed')


def getOtcDecap(num):
    url = 'https://www.tpex.org.tw/web/stock/exright/decap/decap_result.php?l=zh-tw'
    try:
        res = requests.get(url, headers=hd)
        jdata = json.loads(res.text)
        if 'aaData' in jdata:
            all_data = jdata['aaData']
        else:
            with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
                wr = csv.writer(ef)
                wr.writerow(['otc除權息網址的key已改變', datetime.now()])
                # print('otc除權息網址的key已改變')
            return 0
    except Exception as err:
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as ef:
            wr = csv.writer(ef)
            wr.writerow([err, url, datetime.now()])
            print(err)
        if num <= 10:
            num += 1
            time.sleep(num + 15)
            return getCapRed(num)
        else:
            raise err
    else:
        for Data in all_data:
            if Data[0] in code_lt:
                data_lt = []
                for i in range(len(Data)):
                    data_lt.append(Data[i])
                with open(r"D:\2016_2019\msg\OtcDecap.txt", newline='\n', encoding='utf-8') as cr:
                    chk = list(csv.reader(cr))
                if data_lt not in chk:
                    with open(r"D:\2016_2019\msg\OtcDecap.txt", 'a', newline='\n', encoding='utf-8') as cr:
                        wr = csv.writer(cr)
                        wr.writerow(data_lt)
                        print('Done_OtcDeCap')
                else:
                    print('Data existed')


def getFut(url, name, tdy, n):
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}
    all_data = {
        'queryStartDate': tdy,
        'queryEndDate': tdy}
    try:
        res = requests.post(url, headers=hd, data=all_data)
        fullpath = path.join(fut_path, name)
        with open(fullpath, 'wb') as test:
            for i in res:
                test.write(i)
        print('Done', name)
        return 0
    except:
        traceback.print_exc()
        with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
            erf.write(traceback.format_exc())
        if n <= 10:
            n += 1
            time.sleep(10 + n)
            return getFut(url, name, tdy, n)
        else:
            return 1


def ShowAnnotation(code, file, chk_lt, plot_lt):
    df = pd.read_csv('D:/2016_2019/p/p' + code +
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
                if file[25] == 'b':
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
        k_fraction, sub_fraction, blank, left_space, right_space, bottom_space, top_space = 0.6, 0.4, 0.01, 0.07, 0.02, 0.05, 0.05
        axk = fig.add_axes([left_space, 1 - k_fraction + blank, 1 -
                            left_space - right_space, k_fraction - blank - top_space])
        axv = fig.add_axes([left_space, bottom_space, 1 - left_space -
                            right_space, sub_fraction - bottom_space], sharex=axk)
    else:
        k_fraction, bottom_space, vol_fraction, blank, left_space, right_space, top_space = 0.5, 0.05, 0.2, 0.01, 0.07, 0.02, 0.05
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
    axv.bar(time_lt, df[start_idx:last_idx + 1]['vol'], width=0.6,
            linewidth=0, color='#09e8dd', alpha=1, label='vol')
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
    all_ma_lt, k1 = [], 0
    for num, ma_day in enumerate(plot_lt[1]):
        ma_type = plot_lt[2][num]
        if type(ma_day) == int and ma_type != '無' and (ma_day, ma_type) not in all_ma_lt:
            all_ma_lt.append((ma_day, ma_type))
            ma_label = str(ma_day) + ma_type
            df[ma_label] = abstract.MA(
                df, timeperiod=ma_day, matype=matype_dict[ma_type])
            axk.plot(time_lt, df[start_idx:last_idx + 1][ma_label], label=ma_label, color=mavcolors[k1],
                     linewidth=0.7)
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
    name = name_lt[code_lt.index(code)]
    axk.set_title(label=name + '（' + str(code) + '）')
    if file != 0:
        if file[25] == 'b':
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


def ScatterPlot(y_axis, x_axis, file):
    rec = pd.read_csv(file, parse_dates=['buy_date', 'sell_date'])
    rec = rec.astype({k: 'float32' for k in rec.columns if k !=
                      'code' and k != 'buy_date' and k != 'sell_date' and k != 'win'})
    if 'cp' not in rec.columns:
        rec['cp'] = rec['sell_p'] / rec['buy_p'] - 1
    if 'win' not in rec.columns:
        rec['win'] = np.zeros((len(rec),), dtype=int)
        for idx in range(len(rec)):
            rec.loc[idx, 'win'] = 1 if rec.loc[idx, 'cp'] > 0 else 0
    rec.to_csv(file, index=False)
    rec = rec.astype({'code': 'int16', 'win': bool})
    rec_win = rec[rec['win'] == True]
    rec_loss = rec[rec['win'] == False]
    slope, intercept, r, p, std_err = stats.linregress(
        rec[x_axis], rec[y_axis])
    plt.close('all')
    fig, ax = plt.subplots()
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    x_name = reverse_select[x_axis] if x_axis != 'cp' else '報酬率'
    y_name = reverse_select[y_axis] if y_axis != 'cp' else '報酬率'
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.title(y_name + " v.s. " + x_name,
              fontsize=12, fontweight="bold")
    plt.scatter(rec_win[x_axis],
                rec_win[y_axis],
                s=3,
                alpha=.7, label='win', c='#ff9a0d')
    plt.scatter(rec_loss[x_axis],
                rec_loss[y_axis],
                s=3,
                alpha=.7, label='loss', c='#09c2e3')
    ax.legend(framealpha=0.7, markerscale=2)
    plt.style.use("ggplot")
    return (slope, intercept, r, p, std_err, plt)


def treeview_sort_column(tv, col, reverse):
    try:
        tree_lt = [(float(tv.set(k, col)), k) for k in tv.get_children('')]
    except Exception as err:
        print(err)
        tree_lt = [(tv.set(k, col), k) for k in tv.get_children('')]
    tree_lt.sort(key=lambda x: x[0], reverse=reverse)  # 排序方式
    for index, (val, k) in enumerate(tree_lt):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


def cp_plot(cp_df_dict):
    plt.close('all')
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('ggplot')
    ax1, ax3 = plt.subplot(2, 1, 1), plt.subplot(2, 1, 2)
    ret_df['DD%'] = ret_df['ret_close'] / ret_df['ret_close'].cummax() - 1
    #ret_df.to_csv('D:/2016_2019/ret_dd.csv', index=False)
    ax1.plot(ret_df['date'], ret_df['ret_cp'] * 100,
             label='大盤', color='#FFDD00', linewidth=1.3)
    ax3.plot(ret_df['date'], ret_df['DD%'] * 100,
             label='大盤', color='#FFDD00', linewidth=1.3)
    # plt.legend(framealpha=0.1)
    key_lt = list(cp_df_dict.keys())
    # plt.title('報酬率走勢圖')
    for name, cp_df in cp_df_dict.items():
        ax1.plot(cp_df['date'], cp_df['total_cp'] * 100, label=name,
                 color=color_lt[key_lt.index(name)], linewidth=1.3)
        ax1.set_ylabel(ylabel='報酬率%')
        plt.setp(ax1.get_xticklabels(), visible=False)
        # plt.grid(True, linestyle="-", color='#AAAAAA', linewidth='1', axis='both', alpha = 0.3)
        # ax1.yaxis.set_major_locator(MultipleLocator(100))
        # ax1.yaxis.set_minor_locator(MultipleLocator(50))
        plt.tick_params(which='major', length=3)
        plt.tick_params(which='minor', length=2)
        ax3.plot(cp_df['date'], cp_df['DD%'] * 100, label=name,
                 color=color_lt[key_lt.index(name)], linewidth=1.3)
        ax3.set_ylabel(ylabel='回撤%')
        plt.tick_params(which='major', length=3)
        # ax2.xaxis.set_minor_locator(AutoMinorLocator())
        years = mdates.YearLocator()  # every year
        # months = mdates.MonthLocator()  # every month
        years_fmt = mdates.DateFormatter('%Y')
        ax3.xaxis.set_major_locator(years)
        ax3.xaxis.set_major_formatter(years_fmt)
        # ax2.xaxis.set_minor_locator(months)
        # plt.grid(True, linestyle="-", color='#AAAAAA', linewidth='1', axis='both', alpha = 0.3)
    handle_lt = [mlines.Line2D([], [], color='#FFDD00', label='大盤')]
    for key in key_lt:
        handle_lt.append(mlines.Line2D(
            [], [], color=color_lt[key_lt.index(key)], label=key))
    plt.legend(handles=handle_lt, framealpha=0.1)
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()


def SortinoRatio(profit_lt, target_cp, risk_free_cp, AR):
    temp_lt = []
    for cp in profit_lt:
        if isinstance(cp, complex):
            cp = cp.real
        x = 0 if cp >= target_cp else 1
        temp_lt.append(x * (cp - target_cp)**2)

    downside_std = (sum(temp_lt) / len(temp_lt))**0.5
    if downside_std != 0:
        return (AR - risk_free_cp) / downside_std
    else:
        return 0


def CalCP(fname, principle, priority, rank, uplimit, mincash, invest):
    df = pd.read_csv(fname, parse_dates=['buy_date', 'sell_date'])
    df['trade_vol'] = np.zeros((len(df),), dtype=int)
    if fname[22] == 'b':
        start_col, end_col, start_p, end_p = 'buy_date', 'sell_date', 'buy_p', 'sell_p'
    else:
        start_col, end_col, start_p, end_p = 'sell_date', 'buy_date', 'sell_p', 'buy_p'
    ret_start_idx = ret_df[ret_df['date'] == min_date].index.to_list()[0]
    money, un_gl_lt, stk_cnt, assets_lt, money_lt, temp_date_lt, drop_lt = principle, [
    ], [], [], [], [], []
    for idx in range(ret_start_idx, len(ret_df)):
        money += invest if idx % 20 == 19 else 0
        un_gl, real_money = 0, money - mincash
        date_now = ret_df.loc[idx, 'date']
        print(date_now, fname[22])
        temp_date_lt.append(date_now)
        # 記錄未實現損益
        cond00 = df[start_col] == date_now
        idx_lt, real_stk_lt = df[cond00].index.to_list(), []
        if idx_lt != []:
            cand_df = df.loc[idx_lt[0]:idx_lt[-1]].sort_values(
                by=select_dict[priority], ascending=True if rank == '由低到高' else False)
            for df_i in cand_df.index.to_list():
                stk, in_p = str(df.loc[df_i, 'code']), float(
                    cand_df.loc[df_i, start_p])
                try:
                    price_df = pd.read_csv(
                        'D:/2016_2019/p/p' + stk + '.csv', parse_dates=['date'])
                except:
                    price_df = pd.read_csv(
                        'D:/2016_2019/p/p1000.csv', parse_dates=['date'])
                pr_idx_lt = price_df[price_df['date']
                                     == date_now].index.to_list()
                if len(pr_idx_lt) != 0:
                    p_idx = pr_idx_lt[0]
                    close_now = price_df.loc[p_idx, 'close']
                    if fname[22] == 'b':
                        unrealized_income, cost = close_now * \
                            (1 - fee - tax), in_p * (fee + 1)
                    else:
                        unrealized_income, cost = (in_p * (1 - (fee + tax)) - close_now * (
                            1 + fee) + in_p * margin) * 1000, in_p * margin * 1000
                    if cost <= uplimit <= real_money:
                        trade_vol = uplimit // cost
                        real_stk_lt.append((stk, date_now, trade_vol))
                    elif uplimit > real_money >= cost:
                        trade_vol = real_money // cost
                        real_stk_lt.append((stk, date_now, trade_vol))
                    else:
                        trade_vol = 0
                        drop_lt.append(df_i)
                    df.loc[df_i, 'chg_amt'] = df.loc[df_i,
                                                     'chg_amt'] * trade_vol
                    df.loc[df_i, 'trade_vol'] = trade_vol if fname[22] == 'b' else 1000 * trade_vol
                    real_cost = cost * trade_vol
                    un_gl += unrealized_income * trade_vol
                    money -= real_cost
        un_gl_lt.append(un_gl)
        stk_cnt.append(len(real_stk_lt))
        cond01 = df[start_col] < date_now
        cond02 = df[end_col] > date_now
        cond03 = df['trade_vol'] > 0
        idx_lt = df[cond01 & cond02 & cond03].index.to_list()
        if idx_lt != []:
            for df_i in idx_lt:
                stk, in_p = str(df.loc[df_i, 'code']), float(
                    df.loc[df_i, start_p])
                try:
                    price_df = pd.read_csv(
                        'D:/2016_2019/p/p' + stk + '.csv', parse_dates=['date'])
                except:
                    price_df = pd.read_csv(
                        'D:/2016_2019/p/p1000.csv', parse_dates=['date'])
                pr_idx_lt = price_df[price_df['date']
                                     == date_now].index.to_list()
                if len(pr_idx_lt) != 0:
                    p_idx = pr_idx_lt[0]
                    close_now, stk_vol = price_df.loc[p_idx,
                                                      'close'], df.loc[df_i, 'trade_vol']
                    if fname[22] == 'b':
                        unrealized_income, cost = close_now * \
                            (1 - fee - tax) * stk_vol, in_p * (fee + 1) * stk_vol
                    else:
                        unrealized_income, cost = (in_p * (1 - (fee + tax)) - close_now * (
                            1 + fee) + in_p * margin) * stk_vol, in_p * stk_vol * margin
                    un_gl += unrealized_income
        # 記錄已實現損益
        cond04 = df[end_col] == date_now
        idx_lt = df[cond03 & cond04].index.to_list()
        if idx_lt != []:
            for df_i in idx_lt:
                stk_vol = df.loc[df_i, 'trade_vol']
                stk_data = (df.loc[df_i, start_p], df.loc[df_i, end_p])
                if fname[22] == 'b':
                    income = stk_data[1] * (1 - fee - tax) * stk_vol
                else:
                    income = stk_data[0] * (margin + 1 - (fee + tax)) * \
                        stk_vol - stk_data[1] * (1 + fee) * stk_vol
                money += income
        money_lt.append(money)
        assets_lt.append(un_gl + money)
    df.drop(drop_lt, inplace=True)
    df.to_csv(fname, index=False, encoding='utf-8')
    global date_lt
    date_lt = temp_date_lt
    #all_lt = [temp_date_lt, un_gl_lt, assets_lt, money_lt, stk_cnt]
    cp_df = pd.DataFrame(data={'date': temp_date_lt, 'un_gl': un_gl_lt,
                               'assets': assets_lt, 'r_assets': money_lt, 'stk_cnt': stk_cnt})
    cp_df['total_cp'] = cp_df['assets'] / principle - 1
    cp_df['DD%'] = (cp_df['assets'] - cp_df['assets'].cummax()
                    ) / cp_df['assets'].cummax()
    cp_df['DD'] = cp_df['assets'] - cp_df['assets'].cummax()
    MDD = min(cp_df['DD%'])
    beta, alpha, r, p, std_err = stats.linregress(ret_df['ret_close'].pct_change()[
        1:], cp_df['assets'].pct_change()[1:])
    cp_df.to_csv('D:/2016_2019/cp/cp' + fname[22:], index=False)
    print('Done cp_df')
    year_tup = divmod(len(date_lt), 240)
    year_cnt, rest_of_the_day = year_tup[0], year_tup[1]
    all_cp_lt, all_dict, all_idx_lt = ['total_cp'], {
        'total_cp': []}, ['AR', 'sortino']
    all_year_cp_dict, AR_dict, sortino_dict = {}, {}, {}
    cp_idx_lt = cp_df.tail(1).index.to_list()
    if len(cp_idx_lt) != 0:
        for col in all_cp_lt:
            year_cp_lt = []
            if year_cnt >= 1:
                for year in range(239, year_cnt * 240, 239):
                    year_cp_lt.append(
                        cp_df.loc[year, col] - cp_df.loc[year - 239, col])
                if rest_of_the_day != 0:
                    last_profit = cp_df.loc[cp_idx_lt[0], col]
                    delta_cp = last_profit - cp_df.loc[year_cnt * 240 - 1, col]
                    year_cp_lt.append(
                        exp(log(1 + delta_cp) * 240 / rest_of_the_day).real - 1)
            else:
                last_profit = cp_df.loc[cp_df.tail(1).index.to_list()[0], col]
                year_cp_lt.append(
                    exp(240 / rest_of_the_day * log(1 + last_profit)).real - 1)
            # 計算年化報酬率
            if len(year_cp_lt) > 1:
                x = 1 + year_cp_lt[0]
                for enum, ycp in enumerate(year_cp_lt[1:]):
                    x = x * (1 + ycp)
                    print(enum, 'x:', x, 'ycp:', ycp)
                factor = 1 / len(year_cp_lt)
                print('x:', x, '；length of year cp lt:',
                      len(year_cp_lt), factor)
                AR = exp(factor * log(x)).real - 1
            else:
                AR = year_cp_lt[-1]
            all_dict[col].append(AR)
            sortino_ratio = SortinoRatio(year_cp_lt, 0.01, 0.01, AR)
            all_dict[col].append(sortino_ratio)
            all_year_cp_dict[col] = year_cp_lt
            AR_dict[col], sortino_dict[col] = AR, sortino_ratio
        all_ratio_df, all_year_cp_df = pd.DataFrame(
            data=all_dict, index=all_idx_lt), pd.DataFrame(data=all_year_cp_dict)
        all_ratio_df.to_csv('D:/2016_2019/cp/RATIO' + fname[22:])
        all_year_cp_df.to_csv('D:/2016_2019/cp/YCP' + fname[22:], index=False)
        print(AR_dict, sortino_dict)
        return (AR_dict, sortino_dict, MDD, alpha, beta)


def select_stk(min_cap=0.0, max_cap=200.0):
    product_lt = []
    for c in code_lt:
        pr_df = pd.read_csv('D:/2016_2019/p/p' + c +
                            '.csv', parse_dates=['date'])
        if len(pr_df) - 1 >= min_idx:
            try:
                capital = capital_df.loc[0, c]
            except:
                product_lt.append(c)
            else:
                if min_cap * 100000000 <= capital <= max_cap * 100000000:
                    product_lt.append(c)
    return product_lt


def backtest_msg(src):
    if src == 'cond':
        messagebox.showwarning('策略回測', '條件不完整，請重新選擇')
    elif src == 'result':
        messagebox.showinfo('策略回測', '無任何商品符合條件')
    elif src == 'value':
        messagebox.showwarning('策略回測', '停利、停損值必須大於0')
    elif src == 'cap':
        messagebox.showwarning('策略回測', '股本不能小於0')
    elif src == 'number':
        messagebox.showwarning('策略回測', '停利、停損、本金和股本欄位必須為數字')
    elif src == 'seq':
        messagebox.showwarning('策略回測', '股本最小值必須小於最大值')
    elif src == 'view':
        messagebox.showwarning('績效檢視', '至少選擇兩個相異的策略')
    elif src == 'option':
        messagebox.showwarning('策略回測', '參數必須為數字')
    elif src == 'indicator':
        messagebox.showwarning('設定', '副圖1 和 副圖2 不能相同')
    elif src == 'ShowTable':
        messagebox.showwarning('績效檢視', '檔案不存在')
    elif src == 'limit not pos int':
        messagebox.showwarning('設定', 'Fast limit和slow limit必須為正數')
    elif src == 'limit seq':
        messagebox.showwarning('設定', 'Fast limit必須大於slow limit')
    elif src == 'limit larger than 1':
        messagebox.showwarning('設定', 'Fast limit和slow limit必須小於1')
    elif src == 'ma not pos int':
        messagebox.showwarning('設定', '均線的週期必須為正整數')
    elif src == 'BB ma not int':
        messagebox.showwarning('設定', '布林通道週期必須為正整數')
    elif src == 'update ok':
        messagebox.showinfo('資料更新', '資料已全部更新')
    elif src == 'start update':
        messagebox.showinfo('資料更新', '開始更新資料庫')
    elif src == 'no record':
        messagebox.showinfo('績效檢視', '無進出場紀錄')
    elif src == 'success set':
        messagebox.showinfo('設定', '成功設為策略')
    elif src == 'success rename':
        messagebox.showinfo('設定', '該策略已重新命名')


def GoSearch(chk_lt, plot_lt, allbox_lt, file):
    reset = False
    for num, chk in enumerate(chk_lt):
        if chk == 1 and num == 0 and plot_lt[0][0] == plot_lt[0][1]:
            backtest_msg('indicator')
            reset = True
        elif chk == 1 and num == 1:
            try:
                plot_lt[0][2] = float(plot_lt[0][2])
                plot_lt[0][3] = float(plot_lt[0][3])
                float01 = plot_lt[0][2]
                float02 = plot_lt[0][3]
            except:
                backtest_msg('limit not pos int')
                reset = True
            else:
                if float01 <= float02:
                    backtest_msg('limit seq')
                    reset = True
                elif float01 < 0 or float02 < 0:
                    backtest_msg('limit not pos int')
                    reset = True
                elif float01 >= 1 or float02 >= 1:
                    backtest_msg('limit larger than 1')
                    reset = True
    if not reset:
        for n, box_lt in enumerate(plot_lt[1:]):
            if n == 0:
                try:
                    intvar_lt = []
                    for e, val in enumerate(plot_lt[1]):
                        if val != '無' and val != '':
                            plot_lt[1][e] = int(val)
                            intvar_lt.append(int(val))
                except Exception as err:
                    backtest_msg('ma not pos int')
                    reset = True
                else:
                    if intvar_lt != []:
                        for val in intvar_lt:
                            if val <= 0:
                                backtest_msg('ma not pos int')
                                reset = True
            elif n == 2:
                if box_lt[0] != '無':
                    try:
                        box_lt[0] = int(box_lt[0])
                        for x in (2, 3, 4):
                            if box_lt[x] != '' and box_lt[x] != '無':
                                box_lt[x] = float(box_lt[x])
                    except Exception as err:
                        backtest_msg('BB ma not int')
                        reset = True
                    else:
                        if box_lt[0] <= 0:
                            backtest_msg('BB ma not int')
                            reset = True
        if not reset:
            with open('D:/stocks/PlotVal.txt', 'w', newline='\n', encoding='utf-8') as pv:
                wr = csv.writer(pv)
                wr.writerow(chk_lt)
                for line in plot_lt:
                    wr.writerow(line)
            SearchPage(chk_lt, plot_lt, file)


def PlotSetting(root, file):
    def click_enter(self):
        GoSearch([ChkVal01.get(), ChkVal02.get(), ChkVal03.get()], [[comPlot01.get(), comPlot02.get(), comPlot03.get(), comPlot04.get()], [
            val.get() for val in MAcombobox_lt], [v.get() for v in MAtypebox_lt], [BB.get() for BB in BBbox_lt]], allbox_lt, file)

    def callback(input):
        if input.isdigit():
            return True
        elif input == '無' or input == '':
            return True
        else:
            return False

    def MAMAcallback(input):
        try:
            if input == '' or input == ' ' or input == '無' or (type(input) == str and len(input) > 1 and '0.' in input):
                return True
            elif (1 > float(input) > 0):
                return True
            else:
                return False
        except Exception as err:
            return False

    def BBcallback(input):
        try:
            if input == '' or input == ' ' or (type(input) == str and len(input) > 1 and str(input)[1] == '.') or input == '無':
                return True
            elif 5 >= float(input) >= 2:
                return True
            else:
                return False
        except Exception as err:
            return False

    def ChangeStatus01(var, indx, mode):
        if ChkVal01.get() == 0:
            comPlot01.config(state='disabled')
            comPlot02.config(state='disabled')
        else:
            comPlot01.config(state='readonly')
            comPlot02.config(state='readonly')

    def ChangeStatus02(var, indx, mode):
        if ChkVal02.get() == 0:
            comPlot03.config(state='disabled')
            comPlot04.config(state='disabled')
        else:
            comPlot03.config(state='normal')
            comPlot04.config(state='normal')
    Setbox = tk.Toplevel()
    title = '設定主圖/副圖'
    Setbox.title(title)
    Setbox.iconbitmap('D:/stocks/stock.ico')
    Setbox.geometry('700x518+306+0')
    root.wm_state('iconic')
    ChkVal01 = tk.IntVar()
    ChkVal02 = tk.IntVar()
    ChkVal03 = tk.IntVar()
    reg = Setbox.register(callback)
    MAMAreg = Setbox.register(MAMAcallback)
    BBreg = Setbox.register(BBcallback)
    SelectFm = tk.LabelFrame(Setbox, text='設定', padx=3, pady=3)
    SelectFm.pack(side=tk.TOP, fill='x', padx=10, pady=3, ipadx=3, ipady=3)
    ChkBtn01 = ttk.Checkbutton(SelectFm, text='新增副圖', variable=ChkVal01)
    ChkBtn01.grid(row=0, column=0, padx=3, pady=3, ipadx=2, ipady=2)
    ChkBtn02 = ttk.Checkbutton(SelectFm, text='新增MESA', variable=ChkVal02)
    ChkBtn02.grid(row=0, column=1, padx=3, pady=3, ipadx=2, ipady=2)
    ChkBtn03 = ttk.Checkbutton(
        SelectFm, text='新增HT trendline', variable=ChkVal03)
    ChkBtn03.grid(row=0, column=2, padx=3, pady=3, ipadx=2, ipady=2)
    SubPlotFm = tk.LabelFrame(Setbox, text='設定副圖', padx=3, pady=3)
    SubPlotFm.pack(side=tk.TOP, fill='x', padx=10, pady=3, ipadx=3, ipady=3)
    PlotLb01 = tk.Label(SubPlotFm, text='副圖1', padx=5, pady=5)
    PlotLb01.grid(row=0, column=0, padx=3, pady=3, ipadx=2, ipady=2)
    comPlot01 = ttk.Combobox(SubPlotFm, width=8, values=[
        'MACD', 'DMI', 'NATR'], state='readonly')
    comPlot01.grid(row=0, column=1, padx=3, pady=3, ipadx=2, ipady=2)
    comPlot01.current(0)
    PlotLb02 = tk.Label(SubPlotFm, text='副圖2', padx=5, pady=5)
    PlotLb02.grid(row=0, column=2, padx=3, pady=3, ipadx=2, ipady=2)
    comPlot02 = ttk.Combobox(SubPlotFm, width=8, values=[
        'MACD', 'DMI', 'NATR'], state='readonly')
    comPlot02.grid(row=0, column=3, padx=3, pady=3, ipadx=2, ipady=2)
    comPlot02.current(1)
    PlotFm = tk.LabelFrame(Setbox, text='設定MESA參數', padx=3, pady=3)
    PlotFm.pack(side=tk.TOP, fill='x', padx=10, pady=3, ipadx=3, ipady=3)
    PlotLb03 = tk.Label(PlotFm, text='Fast limit', padx=5, pady=5)
    PlotLb03.grid(row=0, column=0, padx=3, pady=3, ipadx=2, ipady=2)
    comPlot03 = ttk.Combobox(PlotFm, width=8, values=[
        0.5, 0.6, 0.7], validate='key', validatecommand=(MAMAreg, '%P'))
    comPlot03.grid(row=0, column=1, padx=3, pady=3, ipadx=2, ipady=2)
    comPlot03.current(0)
    PlotLb04 = tk.Label(PlotFm, text='Slow limit', padx=5, pady=5)
    PlotLb04.grid(row=0, column=2, padx=3, pady=3, ipadx=2, ipady=2)
    comPlot04 = ttk.Combobox(PlotFm, width=8, values=[
        0.05, 0.06, 0.07], validate='key', validatecommand=(MAMAreg, '%P'))
    comPlot04.grid(row=0, column=3, padx=3, pady=3, ipadx=2, ipady=2)
    comPlot04.current(0)
    ChkVal01.trace_add('read', ChangeStatus01)
    ChkVal02.trace_add('read', ChangeStatus02)
    LineFm = tk.LabelFrame(Setbox, text='設定均線', padx=3, pady=3)
    LineFm.pack(side=tk.TOP, fill='x', padx=10, pady=3, ipadx=3, ipady=3)
    MAdayLb = tk.Label(LineFm, text='週期日數', padx=5, pady=5)
    MAdayLb.grid(row=0, column=0, padx=5, pady=5, ipadx=2, ipady=2)
    MAtypeLb = tk.Label(LineFm, text='計算方式', padx=5, pady=5)
    MAtypeLb.grid(row=1, column=0, padx=5, pady=5, ipadx=2, ipady=2)
    MAcombobox_lt = []
    MAtypebox_lt = []
    for num in range(4):
        comType = ttk.Combobox(LineFm, width=5, values=[
            'SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'KAMA', 'T3', '無'], state='readonly')
        comType.grid(row=1, column=num + 1, padx=5, pady=5, ipadx=2, ipady=2)
        comMA = ttk.Combobox(LineFm, width=5, values=[
            5, 13, 21, 55, '無'], validate='key', validatecommand=(reg, '%P'))
        comMA.grid(row=0, column=num + 1, padx=5, pady=5, ipadx=2, ipady=2)
        MAcombobox_lt.append(comMA)
        MAtypebox_lt.append(comType)
    BBFm = tk.LabelFrame(Setbox, text='設定布林通道', padx=3, pady=3)
    BBFm.pack(side=tk.TOP, fill='x', padx=10, pady=3, ipadx=3, ipady=3)
    BBdayLb = tk.Label(BBFm, text='週期日數', padx=5, pady=5)
    BBdayLb.grid(row=0, column=0, padx=5, pady=5, ipadx=2, ipady=2)
    comDay = ttk.Combobox(BBFm, width=5, values=[
        21, 20, '無'], validate='key', validatecommand=(reg, '%P'))
    comDay.grid(row=0, column=1, padx=5, pady=5, ipadx=2, ipady=2)
    BBtypeLb = tk.Label(BBFm, text='計算方式', padx=5, pady=5)
    BBtypeLb.grid(row=0, column=2, padx=5, pady=5, ipadx=2, ipady=2)
    comBBtype = ttk.Combobox(BBFm, width=5, values=[
        'SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'KAMA', 'T3', '無'], state='readonly')
    comBBtype.grid(row=0, column=3, padx=5, pady=5, ipadx=2, ipady=2)
    DevLb = tk.Label(BBFm, text='標準差倍數', padx=5, pady=5)
    DevLb.grid(row=0, column=4, padx=5, pady=5, ipadx=2, ipady=2)
    comDev01 = ttk.Combobox(BBFm, width=3, values=[
        2.1, 2.5, 2.9, 3, '無'], validate='key', validatecommand=(BBreg, '%P'))
    comDev01.grid(row=0, column=5, padx=5, pady=5, ipadx=2, ipady=2)
    comDev02 = ttk.Combobox(BBFm, width=3, values=[
        2.5, 2.9, 3, '無'], validate='key', validatecommand=(BBreg, '%P'))
    comDev02.grid(row=0, column=6, padx=5, pady=5, ipadx=2, ipady=2)
    comDev03 = ttk.Combobox(BBFm, width=3, values=[
        2.9, 3, '無'], validate='key', validatecommand=(BBreg, '%P'))
    comDev03.grid(row=0, column=7, padx=5, pady=5, ipadx=2, ipady=2)
    checkval_lt = [ChkVal01, ChkVal02, ChkVal03]
    for val in checkval_lt:
        val.set(1)
    complotbox_lt = [comPlot01, comPlot02, comPlot03, comPlot04]
    BBbox_lt = [comDay, comBBtype, comDev01, comDev02, comDev03]
    allbox_lt = [complotbox_lt, MAcombobox_lt, MAtypebox_lt, BBbox_lt]
    with open('D:/stocks/PlotVal.txt', newline='\n', encoding='utf-8') as plotval:
        val_lt = list(csv.reader(plotval))[-5:]
    for m, row in enumerate(val_lt):
        if m == 0:
            for n, val in enumerate(row):
                if val != checkval_lt[n].get():
                    checkval_lt[n].set(val)
        else:
            for n, val in enumerate(row):
                box = allbox_lt[m - 1][n]
                if val != box.get():
                    box.set(val)
    DestroyBtn = ttk.Button(
        Setbox, text='取消', command=lambda: Setbox.destroy())
    DestroyBtn.pack(side=tk.RIGHT, padx=10, pady=3, ipadx=3, ipady=3)
    EnterBtn = ttk.Button(Setbox, text='確定',
                          command=lambda: GoSearch([ChkVal01.get(), ChkVal02.get(), ChkVal03.get()],
                                                   [[comPlot01.get(), comPlot02.get(), comPlot03.get(), comPlot04.get()], [val.get() for val in MAcombobox_lt],
                                                    [v.get() for v in MAtypebox_lt], [BB.get() for BB in BBbox_lt]], allbox_lt, file))
    EnterBtn.pack(side=tk.RIGHT, padx=10, pady=3, ipadx=3, ipady=3)
    Setbox.bind("<Return>", click_enter)


def SetName(root, fname, mode):
    # def AddtoList(win, fname, st_name):
    with open('D:/stocks/StrategyList.txt', 'r', newline='\n', encoding='utf-8') as slist:
        total_lt = list(csv.reader(slist))
    rd, strat_lt = [row[0] for row in total_lt], [row[1] for row in total_lt]
    local_fname = fname[22:]
    root.destroy()
    if mode == 'add':
        if local_fname not in rd:
            def InputName(local_fname, name):
                if name not in strat_lt:
                    with open('D:/stocks/StrategyList.txt', 'a', newline='\n', encoding='utf-8') as slist:
                        wr = csv.writer(slist)
                        wr.writerow([local_fname, name])
                    Table.destroy()
                    messagebox.showinfo('設定', '成功設為選股策略')
                else:
                    messagebox.showwarning('設定', '該名稱和其他策略相同，請重新命名')

            def click_enter(self):
                InputName(local_fname, entry_win.get())
            Table = tk.Toplevel()
            Table.title('設定策略名稱')
            Table.iconbitmap('D:/stocks/stock.ico')
            Table.geometry('400x50+300+200')
            tk.Label(Table, text='策略名稱:').grid(
                row=0, column=0, padx=6, pady=6, ipadx=2, ipady=2)
            entry_win = ttk.Entry(Table, width=18)
            entry_win.grid(row=0, column=1, padx=6, pady=6, ipadx=2, ipady=2)
            ttk.Button(Table, text='確定', command=lambda: InputName(
                local_fname, entry_win.get())).grid(row=0, column=2, padx=6, pady=6, ipadx=2, ipady=2)
            entry_win.bind("<Return>", click_enter)

        else:
            messagebox.showinfo('設定', '該策略已存在')
    else:
        if local_fname in rd:
            del total_lt[rd.index(local_fname)]
            with open('D:/stocks/StrategyList.txt', 'w', newline='\n', encoding='utf-8') as slist:
                wr = csv.writer(slist)
                for item in total_lt:
                    wr.writerow(item)
            messagebox.showinfo('設定', '成功刪除策略')
        else:
            messagebox.showwarning('設定', '該策略不存在')


def Analysis(root, fname):
    def confirm_axis(y, x, fname):
        if x == y:
            messagebox.showwarning('數據分析', '橫軸和縱軸必須相異')
        else:
            plot_rtn = ScatterPlot(axis_dict[y], axis_dict[x], fname)
            plt_table = tk.Toplevel()
            plt_table.title(fname)
            plt_table.geometry('360x280+770+10')
            plt_table.iconbitmap('D:/stocks/stock.ico')
            col_tup = ('斜率:', '截距:', 'R:', 'p-value:', '標準差:')
            plot_fm = tk.LabelFrame(
                plt_table, text=y + 'v.s.' + x, padx=8, pady=8)
            plot_fm.pack(side=tk.TOP, fill='both',
                         padx=8, pady=8, ipadx=4, ipady=4)
            for e, val in enumerate(plot_rtn[:-1]):
                tk.Label(plot_fm, text=col_tup[e]).grid(
                    row=e, column=0, padx=6, pady=6, ipadx=2, ipady=2)
                tk.Label(plot_fm, text=round(val, 6) if e != 3 else val).grid(
                    row=e, column=1, padx=6, pady=6, ipadx=2, ipady=2)
            plot_rtn[-1].show()

    def click_enter(self):
        confirm_axis(comY.get(), comX.get(), fname)
    root.destroy()
    Table = tk.Toplevel()
    title = fname
    Table.title(title)
    Table.iconbitmap('D:/stocks/stock.ico')
    Table.geometry('300x196+300+10')
    TableFm = tk.LabelFrame(Table, text='選擇坐標軸', padx=8, pady=8)
    TableFm.pack(side=tk.TOP, fill='both', padx=8, pady=8, ipadx=4, ipady=4)
    new_dict = {'報酬率': 'cp'}
    axis_dict = {**new_dict, **select_dict}
    axis_tup = tuple(axis_dict)
    tk.Label(TableFm, text='選擇縱軸').grid(
        row=0, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comY = ttk.Combobox(TableFm, width=13, values=axis_tup, state='readonly')
    comY.grid(row=0, column=1, padx=6, pady=6, ipadx=2, ipady=2)
    tk.Label(TableFm, text='選擇橫軸').grid(
        row=1, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comX = ttk.Combobox(TableFm, width=13, values=axis_tup, state='readonly')
    comX.grid(row=1, column=1, padx=6, pady=6, ipadx=2, ipady=2)
    ttk.Button(TableFm, text='作圖', command=lambda: confirm_axis(comY.get(), comX.get(
    ), fname)).grid(row=2, column=0, columnspan=2, padx=6, pady=6, ipadx=2, ipady=2)
    Table.bind('<Return>', click_enter)


def Annotate(root, fname):
    RecTable = tk.Toplevel()
    title = fname + '（多單）' if fname[22] == 'b' else fname + '（空單）'
    RecTable.title(title)
    RecTable.iconbitmap('D:/stocks/stock.ico')
    RecTable.geometry('860x550+0+0')
    root.wm_state('iconic')
    TableFm = tk.LabelFrame(RecTable, text='詳細資料', padx=8, pady=8)
    TableFm.pack(side=tk.TOP, fill='x', padx=6, pady=6, ipadx=4, ipady=4)
    EntryFm = tk.LabelFrame(RecTable, padx=8, pady=8)
    EntryFm.pack(side=tk.TOP, fill='x', padx=6, pady=6, ipadx=4, ipady=4)
    with open('D:/stocks/StrategyList.txt', newline='\n', encoding='utf-8') as slist:
        all_lt = [row[0] for row in csv.reader(slist)]
    if fname[22:] not in all_lt:
        mode = 'add'
        btn_txt = '設為選股策略'
    else:
        mode = 'remove'
        btn_txt = '刪除策略'
    ttk.Button(EntryFm, text='查看K線圖', command=lambda: PlotSetting(
        RecTable, 'D:/2016_2019/rawbacktest/' + fname[22:])).grid(row=0, column=0, padx=4, pady=4, ipadx=2, ipady=2)
    ttk.Button(EntryFm, text='數據分析', command=lambda: Analysis(
        RecTable, 'D:/2016_2019/rawbacktest/' + fname[22:])).grid(row=0, column=1, padx=4, pady=4, ipadx=2, ipady=2)
    ttk.Button(EntryFm, text=btn_txt, command=lambda: SetName(
        RecTable, fname, mode)).grid(row=0, column=2, padx=4, pady=4, ipadx=2, ipady=2)
    vbar = tk.Scrollbar(TableFm, orient='vertical',
                        takefocus=1, cursor='hand2')
    tree = ttk.Treeview(TableFm, height=18, column=("2", "3", "4", "5", "6", "7", "8", "9"),
                        yscrollcommand=vbar.set)
    vbar.config(command=tree.yview)
    tree.column("#0", width=25, minwidth=25)
    tree.column("2", width=25, minwidth=25)
    tree.column("3", width=60)
    tree.column("4", width=35)
    tree.column("5", width=60)
    tree.column("6", width=35)
    tree.column("7", width=35)
    tree.column("8", width=35)
    tree.column("9", width=70)
    tree.heading("#0", text='代碼', anchor=tk.W)
    tree.heading("2", text='名稱', anchor=tk.W)
    tree.heading("3", text='進場日期', anchor=tk.W)
    tree.heading("4", text='進場價格', anchor=tk.W)
    tree.heading("5", text='出場日期', anchor=tk.W)
    tree.heading("6", text='出場價格', anchor=tk.W)
    tree.heading("7", text='報酬率%', anchor=tk.W)
    tree.heading("8", text='持有天數', anchor=tk.W)
    tree.heading("9", text='幾何報酬率%', anchor=tk.W)
    df = pd.read_csv(fname, parse_dates=['buy_date', 'sell_date'])
    in_date, out_date = 'buy_date' if fname[22] == 'b' else 'sell_date', 'buy_date' if fname[22] == 's' else 'sell_date'
    in_price, out_price = 'buy_p' if fname[22] == 'b' else 'sell_p', 'buy_p' if fname[22] == 's' else 'sell_p'
    for i in range(len(df)):
        stk = str(df.loc[i, 'code'])
        days = str(df.loc[i, 'days'])
        for enum, n in enumerate(days):
            if n == ' ':
                days = days[:enum]
                break
        tree.insert("", i, text=stk, values=(name_lt[code_lt.index(stk)], df.loc[i, in_date].strftime('%Y-%m-%d'), round(df.loc[i, in_price], 2),
                                             df.loc[i, out_date].strftime('%Y-%m-%d'), round(df.loc[i, out_price], 2), round(df.loc[i, 'cp'] * 100, 2), days, round(df.loc[i, 'ar'] * 100, 2)),
                    tag='red' if df.loc[i, 'cp'] > 0 else 'green')
    tree.tag_configure('red', font=tkfont.nametofont(
        'TkTextFont'), foreground='#ff0089')
    tree.tag_configure('green', font=tkfont.nametofont(
        'TkTextFont'), foreground='#008b8b')
    vbar.pack(fill='y', side=tk.RIGHT, padx=5, pady=5)
    tree.pack(fill='both', padx=5, pady=5, ipadx=2, ipady=2)


def select(file_name):
    if file_name[0] == 'b':
        direction = 'BullIn'
        out_direction = 'BullOut'
        in_date = 'buy_date'
        out_date = 'sell_date'
        in_p = 'buy_p'
        out_p = 'sell_p'
        record = pd.read_csv('D:/stocks/BullCol.csv').astype(
            {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    else:
        direction = 'BearIn'
        out_direction = 'BearOut'
        in_date = 'sell_date'
        out_date = 'buy_date'
        in_p = 'sell_p'
        out_p = 'buy_p'
        record = pd.read_csv('D:/stocks/BearCol.csv').astype(
            {'code': 'int16', 'sell_date': 'datetime64', 'buy_date': 'datetime64'})
    rec_df = pd.read_csv('D:/stocks/Rec.csv',  encoding='utf-8')
    idx_lt, exe_lt = rec_df['name'][rec_df['name'] == file_name].index.to_list(), [
    ]
    if len(idx_lt) != 0:
        mincap, maxcap = rec_df.loc[idx_lt[0],
                                    'mincap'], rec_df.loc[idx_lt[0], 'maxcap']
        if mincap != 0 or maxcap != 200:
            if mincap == 0 and maxcap >= 2593.04:
                with open('D:/stocks/below200.txt', newline='\n', encoding='utf-8') as b200:
                    lastb200 = list(csv.reader(b200))[-1][0]
                last_cd_idx = code_lt.index(lastb200)
                for c_num, cd in enumerate(code_lt):
                    if c_num <= last_cd_idx:
                        exe_lt.append(cd)
            else:
                exe_lt = select_stk(mincap, maxcap)
        else:
            with open('D:/stocks/below200.txt', newline='\n', encoding='utf-8') as b200:
                reader = list(csv.reader(b200))
                for row in reader:
                    exe_lt.append(row[0])
        idx, sl, tp = idx_lt[0], rec_df.loc[idx_lt[0],
                                            'sl'], rec_df.loc[idx_lt[0], 'tp']
        in_tup, out_tup = tuple(rec_df.loc[idx, 'in' + str(num)] for num in range(
            6)), tuple(rec_df.loc[idx, 'out' + str(num)] for num in range(6))
        MonAmt, mincp = rec_df.loc[idx, 'monamt'], rec_df.loc[idx, 'mincp']
        with open('D:/stocks/tdy_done.txt', newline='\n', encoding='utf-8') as tdydone_list:
            last_tdy_done = list(csv.reader(tdydone_list))[-1][0]
        for code in exe_lt:
            in_name = strategy_lt[int(file_name[1:3])]
            in_df = opt_dict.get(in_name)(code, direction, sl, tp, sl, tp, [], [
            ], in_tup[0], in_tup[1], in_tup[2], in_tup[3], in_tup[4], in_tup[5], MonAmt, mincp, 'select')
            if len(in_df) != 0:
                record = record.append(in_df, ignore_index=True, sort=False)
                print(file_name[0], code, name_lt[code_lt.index(code)])
        if file_name in listdir('D:/2016_2019/shareholding'):
            with open('D:/stocks/fix_price.txt', newline='\n', encoding='utf-8') as fixf:
                fixed_lt = list(csv.reader(fixf))
            sharehold_df = pd.read_csv(
                'D:/2016_2019/shareholding/' + file_name, parse_dates=['buy_date', 'sell_date'])
            check_lt, result_code_lt = ['OtcDivResult.txt',
                                        'OtcDecapResult.txt', 'DivResult.txt', 'DecapResult.txt'], []
            for file_title in check_lt:
                with open('D:/2016_2019/msg/' + file_title, newline='\n', encoding='utf-8') as result_f:
                    result_lt = list(csv.reader(result_f))
                    for result_row in result_lt:
                        if file_title == 'OtcDivResult.txt' or file_title == 'DecapResult.txt':
                            result_date_lt = result_row[0].split('/')
                            date_str = str(
                                int(result_date_lt[0]) + 1911) + result_date_lt[1] + result_date_lt[2]
                            if date_str == tdy and [date_str, result_row[1]] not in fixed_lt:
                                result_code_lt.append(result_row[1])
                        elif file_title == 'OtcDecapResult.txt':
                            result_date_lt = result_row[0]
                            date_str = str(
                                int(result_date_lt[:3]) + 1911) + result_date_lt[3:5] + result_date_lt[5:]
                            if date_str == tdy and [date_str, result_row[1]] not in fixed_lt and result_row[1] not in result_code_lt:
                                result_code_lt.append(result_row[1])
                        else:
                            result_date_lt = result_row[0]
                            date_str = str(
                                int(result_date_lt[:3]) + 1911) + result_date_lt[4:6] + result_date_lt[7:9]
                            if date_str == tdy and [date_str, result_row[1]] not in fixed_lt and result_row[
                                    1] not in result_code_lt:
                                result_code_lt.append(result_row[1])
            for i in range(len(sharehold_df)):
                if sharehold_df.loc[i, out_date] == end:
                    hold_code = str(sharehold_df.loc[i, 'code'])
                    if hold_code in result_code_lt and sharehold_df.loc[i, in_date] < datetime_tdy:
                        check_price = pd.read_csv(
                            'D:/2016_2019/p/p' + hold_code + '.csv', parse_dates=['date'])
                        if check_price[check_price['date'] == sharehold_df.loc[i, in_date]].index.to_list() != []:
                            chk_idx = check_price[check_price['date'] == sharehold_df.loc[i, in_date]].index.to_list()[
                                0]
                            sharehold_df.loc[i,
                                             in_p] = check_price.loc[chk_idx, 'close']
                    out_name = strategy_lt[int(file_name[3:5])]
                    sent_df = sharehold_df.loc[[i]]
                    sent_df.reset_index(drop=True, inplace=True)
                    if 'Unnamed: 0' in sent_df.columns:
                        sent_df.drop(columns=['Unnamed: 0'], inplace=True)
                    out_df = opt_dict.get(out_name)(hold_code, out_direction, sl, tp, sl, tp, sent_df, sent_df,
                                                    out_tup[0], out_tup[1], out_tup[2], out_tup[3], out_tup[4], out_tup[5], MonAmt, mincp, 'select')
                    if out_df.loc[0, out_date] != end:
                        sharehold_df.loc[i, out_date], sharehold_df.loc[i,
                                                                        out_p] = out_df.loc[0, out_date], out_df.loc[0, out_p]
                        sharehold_df = sharehold_df.astype(
                            {'code': 'int16', 'buy_date': 'datetime64', 'sell_date': 'datetime64'})
            sharehold_df = sharehold_df.append(
                record, ignore_index=True, sort=False)
            sharehold_df.to_csv(
                'D:/2016_2019/shareholding/' + file_name, index=False)
            with open('D:/stocks/select_done.txt', 'a', newline='\n', encoding='utf-8') as select_list:
                wr_s = csv.writer(select_list)
                wr_s.writerow([file_name, last_tdy_done])
        else:
            record.to_csv('D:/2016_2019/shareholding/' +
                          file_name, index=False)
            with open('D:/stocks/select_done.txt', 'a', newline='\n', encoding='utf-8') as select_list:
                wr_s = csv.writer(select_list)
                wr_s.writerow([file_name, last_tdy_done])


def ShowResult(bull_name, bear_name, bull_exist, bear_exist, principle_dict, select_priority, group_dict, root):
    table_lt, file_lt, win_loss_dict, col_tup, gain_len, loss_len = [{}, {}, {}], [bull_name, bear_name], {
        'bull_win': 0, 'bull_loss': 0, 'bear_win': 0, 'bear_loss': 0}, ('多', '空'), 0, 0
    for table in table_lt:
        for heading in heading_lt:
            table[heading] = 'N/A'
    if bull_exist and bear_exist:
        for file_id, file in enumerate(file_lt):
            if type(root) != str:
                root.destroy()
            principle_key = col_tup[file_id] + '單本金'
            priority = col_tup[file_id] + '單篩選依據'
            seq = col_tup[file_id] + '單排序'
            uplimit = col_tup[file_id] + '單金額上限'
            mincash = col_tup[file_id] + '單最低現金'
            invest = col_tup[file_id] + '單投入金額'
            rtn_tup = CalCP(file, principle_dict[principle_key], select_priority[priority],
                            select_priority[seq], group_dict[uplimit], group_dict[mincash], group_dict[invest])
            trade_df = pd.read_csv(file, parse_dates=['buy_date', 'sell_date'])
            win_df = trade_df[trade_df['win'] == 1]
            TradeCnt, WinCnt = len(trade_df), len(win_df)
            LossCnt, odds = TradeCnt - WinCnt, WinCnt / TradeCnt
            MaxCP, MinCP, MaxAR, MinAR = max(trade_df['cp']), min(trade_df['cp']), max(trade_df['ar']), min(
                trade_df['ar'])
            cnt_dict, win_cnt_dict, loss_cnt_dict = {}, {}, {}
            for j in range(int_year_ini, int_year_now + 1):
                cnt_dict[str(j)], win_cnt_dict[str(
                    j)], loss_cnt_dict[str(j)] = {}, {}, {}
                for k in range(1, 13):
                    cnt_dict[str(j)][str(k)] = 0
                    win_cnt_dict[str(j)][str(k)] = 0
                    loss_cnt_dict[str(j)][str(k)] = 0
            type_dict = {'b': ('bull', 'sell_date'), 's': ('bear', 'buy_date')}
            for m in range(len(trade_df)):
                amt = trade_df.loc[m, 'chg_amt']
                trade_date = trade_df.loc[m, type_dict[file[22]][1]]
                year, mon = trade_date.strftime(
                    '%Y'), trade_date.strftime('%m')
                mon = mon[1] if mon[0] == '0' else mon
                cnt_dict[year][mon] += 1
                if trade_df.loc[m, 'win'] == 1:
                    win_cnt_dict[year][mon] += 1
                else:
                    loss_cnt_dict[year][mon] += 1
            total_ar, total_sortino = rtn_tup[0]['total_cp'], rtn_tup[1]['total_cp']
            cp_df = pd.read_csv('D:/2016_2019/cp/cp' +
                                file[22:], parse_dates=['date'])
            MDD, alpha, beta = rtn_tup[2], rtn_tup[3], rtn_tup[4]
            earn, loss, last_earn, last_loss = 0, 0, True, True
            earn_lt, loss_lt = [], []
            for cpi in range(1, len(cp_df)):
                if cp_df.loc[cpi, 'total_cp'] > cp_df.loc[cpi - 1, 'total_cp'] and last_earn:
                    earn += cp_df.loc[cpi, 'total_cp'] - \
                        cp_df.loc[cpi - 1, 'total_cp']
                elif cp_df.loc[cpi, 'total_cp'] > cp_df.loc[cpi - 1, 'total_cp'] and last_earn == False:
                    earn = cp_df.loc[cpi, 'total_cp'] - \
                        cp_df.loc[cpi - 1, 'total_cp']
                    last_earn = True
                    last_loss = False
                else:
                    earn_lt.append(earn)
                    last_earn = False
                    last_loss = True
                    loss = cp_df.loc[cpi, 'total_cp'] - \
                        cp_df.loc[cpi - 1, 'total_cp']
                if cp_df.loc[cpi, 'total_cp'] < cp_df.loc[cpi - 1, 'total_cp'] and last_loss:
                    loss += cp_df.loc[cpi, 'total_cp'] - \
                        cp_df.loc[cpi - 1, 'total_cp']
                elif cp_df.loc[cpi, 'total_cp'] < cp_df.loc[cpi - 1, 'total_cp'] and last_loss == False:
                    loss = cp_df.loc[cpi, 'total_cp'] - \
                        cp_df.loc[cpi - 1, 'total_cp']
                    last_loss = True
                    last_earn = False
                else:
                    loss_lt.append(loss)
                    last_loss = False
                    last_earn = True
                    earn = cp_df.loc[cpi, 'total_cp'] - \
                        cp_df.loc[cpi - 1, 'total_cp']
            final_cp = cp_df.loc[cp_df.tail(1).index.to_list()[0], 'total_cp']
            avg_cp = final_cp / TradeCnt
            gdf, ldf = trade_df[trade_df['chg_amt'] >
                                0]['chg_amt'], trade_df[trade_df['chg_amt'] <= 0]['chg_amt']
            if not gdf.empty and not ldf.empty:
                gain, loss = gdf.sum(), ldf.sum()
                gain_len += len(gdf)
                loss_len += len(ldf)
                glr = abs((gain / len(gdf)) / (loss / len(ldf)))
            elif not gdf.empty and ldf.empty:
                gain, loss = gdf.sum(), 0
                gain_len += len(gdf)
                glr = np.NaN
            elif gdf.empty and not ldf.empty:
                gain, loss = 0, ldf.sum()
                loss_len += len(ldf)
                glr = 0
            else:
                raise ValueError
            win_loss_dict[type_dict[file[22]][0] + '_win'] = gain
            win_loss_dict[type_dict[file[22]][0] + '_loss'] = loss
            result_dict = {'總交易次數': TradeCnt, '獲利次數': WinCnt, '虧損次數': LossCnt, '勝率%': odds,
                           '單筆最高報酬率%': MaxCP, '單筆最低報酬率%': MinCP, '年化報酬率%': total_ar, '單日最大獲利率%': max(cp_df['assets'].pct_change()[1:]),
                           '最大回撤%': MDD, '單日最大虧損率%': min(cp_df['assets'].pct_change()[1:]), '最大連續獲利率%': max(earn_lt), '最大連續虧損率%': min(loss_lt),
                           '單筆最高幾何報酬率%': MaxAR, '單筆最低幾何報酬率%': MinAR, '總報酬率%': final_cp, '平均報酬率%': avg_cp,
                           'Sortino ratio': round(total_sortino, 4), 'cnt_dict': cnt_dict, 'win_cnt_dict': win_cnt_dict, 'loss_cnt_dict': loss_cnt_dict,
                           '賺賠比': round(glr, 3), 'alpha': round(alpha, 2), 'beta': round(beta, 2)}
            for e, heading in enumerate(heading_lt):
                table_lt[file_id][heading] = result_dict[heading] if (
                    0 <= e <= 2 or e >= 16) else round(100 * result_dict[heading], 2)
        total_earn_cnt = table_lt[0]['獲利次數'] + table_lt[1]['獲利次數']
        total_trade_cnt = table_lt[0]['總交易次數'] + table_lt[1]['總交易次數']
        total_loss_cnt = table_lt[0]['虧損次數'] + table_lt[1]['虧損次數']
        total_maxcp, total_mincp, total_maxar, total_minar = max(table_lt[0]['單筆最高報酬率%'], table_lt[1]['單筆最高報酬率%']), min(table_lt[0]['單筆最低報酬率%'], table_lt[1]['單筆最低報酬率%']), max(
            table_lt[0]['單筆最高幾何報酬率%'], table_lt[1]['單筆最高幾何報酬率%']), min(table_lt[0]['單筆最低幾何報酬率%'], table_lt[1]['單筆最低幾何報酬率%'])
        bull_cpdf = pd.read_csv('D:/2016_2019/cp/cp' +
                                file_lt[0][22:], parse_dates=['date'])
        bear_cpdf = pd.read_csv('D:/2016_2019/cp/cp' +
                                file_lt[1][22:], parse_dates=['date'])
        total_assets_sum, total_r_assets_sum = bull_cpdf['assets'] + \
            bear_cpdf['assets'], bull_cpdf['r_assets'] + bear_cpdf['r_assets']
        total_cp, stk_cnt = total_assets_sum / \
            (principle_dict['多單本金'] + principle_dict['空單本金']) - \
            1, bull_cpdf['stk_cnt'] + bear_cpdf['stk_cnt']
        total_df = pd.DataFrame(data={'date': date_lt, 'assets': total_assets_sum, 'r_assets': total_r_assets_sum,
                                      'total_cp': total_cp, 'stk_cnt': stk_cnt})
        total_beta, total_alpha, r, p, std_err = stats.linregress(
            ret_df['ret_close'].pct_change()[1:], total_df['assets'].pct_change()[1:])
        total_df['DD'] = total_df['assets'] - total_df['assets'].cummax()
        total_df['DD%'] = total_df['DD'] / total_df['assets'].cummax()
        total_MDD = total_df['DD%'].min()
        total_name = 'total' + file_lt[0][22:27] + \
            file_lt[1][22:27] + file_lt[0][27:]
        total_df.to_csv('D:/2016_2019/cp/' + total_name, index=False)
        year_cp_lt, year_cnt_tup = [], divmod(len(total_cp), 240)
        if year_cnt_tup[0] >= 1:
            for year in range(239, year_cnt_tup[0] * 240, 239):
                year_cp_lt.append(
                    total_df.loc[year, 'total_cp'] - total_df.loc[year - 239, 'total_cp'])
            if year_cnt_tup[1] != 0:
                last_profit = total_df.loc[total_df.tail(
                    1).index.to_list()[0], 'total_cp']
                delta_cp = last_profit - \
                    total_df.loc[year_cnt_tup[0] * 240 - 1, 'total_cp']
                year_cp_lt.append(
                    exp(240 / year_cnt_tup[1] * log(1 + delta_cp)).real - 1)
        else:
            last_profit = total_df.loc[total_df.tail(
                1).index.to_list()[0], 'total_cp']
            year_cp_lt.append(
                exp(240 / year_cnt_tup[1] * log(1 + last_profit)).real - 1)
        # 計算年化報酬率
        if len(year_cp_lt) > 1:
            x = 1 + year_cp_lt[0]
            print('First:', x)
            for enum, ycp in enumerate(year_cp_lt[1:]):
                x = x * (1 + ycp)
                print(enum, 'x:', x, '；ycp:', ycp)
            total_AR = exp(log(x) / len(year_cp_lt)).real - 1
            print('total AR:', total_AR)
        else:
            total_AR = year_cp_lt[-1]
        earn, loss, last_earn, last_loss = 0, 0, True, True
        earn_lt, loss_lt = [], []
        for cpi in range(1, len(total_df)):
            if total_df.loc[cpi, 'total_cp'] > total_df.loc[cpi - 1, 'total_cp'] and last_earn:
                earn += total_df.loc[cpi, 'total_cp'] - \
                    total_df.loc[cpi - 1, 'total_cp']
            elif total_df.loc[cpi, 'total_cp'] > total_df.loc[cpi - 1, 'total_cp'] and last_earn == False:
                earn = total_df.loc[cpi, 'total_cp'] - \
                    total_df.loc[cpi - 1, 'total_cp']
                last_earn = True
                last_loss = False
            else:
                earn_lt.append(earn)
                last_earn = False
                last_loss = True
                loss = total_df.loc[cpi, 'total_cp'] - \
                    total_df.loc[cpi - 1, 'total_cp']
            if total_df.loc[cpi, 'total_cp'] < total_df.loc[cpi - 1, 'total_cp'] and last_loss:
                loss += total_df.loc[cpi, 'total_cp'] - \
                    total_df.loc[cpi - 1, 'total_cp']
            elif total_df.loc[cpi, 'total_cp'] < total_df.loc[cpi - 1, 'total_cp'] and last_loss == False:
                loss = total_df.loc[cpi, 'total_cp'] - \
                    total_df.loc[cpi - 1, 'total_cp']
                last_loss = True
                last_earn = False
            else:
                loss_lt.append(loss)
                last_loss = False
                last_earn = True
                earn = total_df.loc[cpi, 'total_cp'] - \
                    total_df.loc[cpi - 1, 'total_cp']
        total_idx_lt = total_df.tail(1).index.to_list()
        final_total_cp = total_df.loc[total_idx_lt[0],
                                      'total_cp'] if total_idx_lt != [] else 0
        avg_total_cp, total_sortino = final_total_cp / \
            total_trade_cnt, SortinoRatio(total_cp, 0.01, 0.01, total_AR)
        cnt_dict, win_cnt_dict, loss_cnt_dict = {}, {}, {}
        for j in range(int_year_ini, int_year_now + 1):
            cnt_dict[str(j)], win_cnt_dict[str(
                j)], loss_cnt_dict[str(j)] = {}, {}, {}
            for k in range(1, 13):
                cnt_dict[str(j)][str(k)] = 0
                win_cnt_dict[str(j)][str(k)] = 0
                loss_cnt_dict[str(j)][str(k)] = 0
        for m in range(1, len(total_df)):
            year, mon = total_df.loc[m, 'date'].strftime(
                '%Y'), total_df.loc[m, 'date'].strftime('%m')
            mon = mon[1] if mon[0] == '0' else mon
            cnt_dict[year][mon] += 1
            if total_df.loc[m, 'total_cp'] > total_df.loc[m - 1, 'total_cp']:
                win_cnt_dict[year][mon] += 1
            else:
                loss_cnt_dict[year][mon] += 1
        if gain_len != 0 and loss_len != 0:
            per_gain, per_loss = (win_loss_dict['bull_win'] + win_loss_dict['bear_win']) / gain_len, (win_loss_dict['bull_loss'] + win_loss_dict['bear_loss']) / loss_len
            total_winloss_ratio = per_gain / per_loss
        elif gain_len == 0 and loss_len != 0:
            total_winloss_ratio = 0
        else:
            total_winloss_ratio = 10000
        result_dict = {'總交易次數': total_trade_cnt, '獲利次數': total_earn_cnt, '虧損次數': total_loss_cnt,
                       '勝率%': total_earn_cnt / total_trade_cnt * 100, '單筆最高報酬率%': total_maxcp, '單筆最低報酬率%': total_mincp, '年化報酬率%': total_AR * 100, '單日最大獲利率%': max(total_df['assets'].pct_change()[1:]) * 100,
                       '最大回撤%': total_MDD * 100, '單日最大虧損率%': min(total_df['assets'].pct_change()[1:]) * 100, '最大連續獲利率%': max(earn_lt) * 100, '最大連續虧損率%': min(loss_lt) * 100,
                       '單筆最高幾何報酬率%': total_maxar, '單筆最低幾何報酬率%': total_minar, '總報酬率%': final_total_cp * 100, '平均報酬率%': avg_total_cp * 100, 'Sortino ratio': total_sortino,
                       'cnt_dict': 0, 'win_cnt_dict': 0, 'loss_cnt_dict': 0, '賺賠比': total_winloss_ratio,
                       'alpha': total_alpha, 'beta': total_beta}
        for e, heading in enumerate(heading_lt):
            table_val = result_dict[heading]
            table_lt[2][heading] = table_val if type(
                table_val) == int else round(table_val, 2)
        cnt_dict_lt, save_lt = [], []
        for key in ('cnt_dict', 'win_cnt_dict', 'loss_cnt_dict'):
            all_cnt_dict = {}
            for y in range(int_year_ini, int_year_now + 1):
                y = str(y)
                all_cnt_dict[y] = {}
                for mon in range(1, 13):
                    mon = str(mon)
                    bull_mon_cnt, bear_mon_cnt = table_lt[0][key][y][mon], table_lt[1][key][y][mon]
                    all_cnt_dict[y][mon] = (
                        bull_mon_cnt, bear_mon_cnt, bull_mon_cnt + bear_mon_cnt)
            cnt_dict_lt.append(all_cnt_dict)
            save_lt.append(all_cnt_dict)
        ResTable = tk.Toplevel()
        ResTable.title(bull_name[22:-4] + '&' + bear_name[22:-4])
        ResTable.geometry('815x505+253+0')
        ResTable.iconbitmap('D:/stocks/stock.ico')
        TableFm = tk.Frame(ResTable)
        TableFm.pack(side=tk.TOP, fill='x', padx=6, pady=6)
        vbar = tk.Scrollbar(TableFm, orient='vertical',
                            takefocus=1, cursor='hand2')
        tree = ttk.Treeview(TableFm, height=20, column=("Column 2", "Column 3", "Column 4"),
                            yscrollcommand=vbar.set)
        vbar.config(command=tree.yview)
        vbar.pack(side=tk.RIGHT, fill='y', padx=5, pady=5, ipadx=2, ipady=2)
        tree.column("#0", width=200)
        tree.column("Column 2", width=150, minwidth=120)
        tree.column("Column 3", width=150, minwidth=120)
        tree.column("Column 4", width=150, minwidth=120)
        tree.heading("#0", text='項目', anchor=tk.W)
        tree.heading("Column 2", text='多單', anchor=tk.W)
        tree.heading("Column 3", text='空單', anchor=tk.W)
        tree.heading("Column 4", text='合併', anchor=tk.W)
        for e, heading in enumerate(heading_lt):
            if e <= 2:
                top_row = tree.insert("", e, text=heading, values=(
                    table_lt[0][heading], table_lt[1][heading], table_lt[2][heading]))
                row_idx = 0
                for cnt_key, cnt_val in cnt_dict_lt[e].items():
                    sec_row = tree.insert(top_row, row_idx, text=cnt_key + '年',
                                          values=(sum(mon_cnt[0] for mon_cnt in cnt_val.values()),
                                                  sum(mon_cnt[1] for mon_cnt in cnt_val.values()), sum(mon_cnt[2] for mon_cnt in cnt_val.values())),
                                          tags=('odd2',) if int(cnt_key) % 2 == 1 else ('even2',))
                    row_idx += 1
                    end_idx = 0
                    for k2, v2 in cnt_val.items():
                        tree.insert(sec_row, 'end', text=k2 + '月', values=v2,
                                    tags=('odd3',) if int(k2) % 2 == 1 else ('even3',))
                        end_idx += 1
            elif e <= 16 or e >= 20:
                for col in range(3):
                    save_lt[col][heading] = table_lt[col][heading]
                if table_lt[0][heading] > 0 and table_lt[1][heading] > 0 and table_lt[2][heading] > 0:
                    tag = ('red',)
                elif table_lt[0][heading] < 0 and table_lt[1][heading] < 0 and table_lt[2][heading] < 0:
                    tag = ('green',)
                else:
                    tag = ('black',)
                tree.insert("", 'end', text=heading, values=(
                    table_lt[0][heading], table_lt[1][heading], table_lt[2][heading]), tags=tag)
        with open('D:/2016_2019/cp/' + total_name[:-4] + '.json', 'w') as jsonfile:
            json.dump(save_lt, jsonfile)
        tree.tag_configure('odd2', font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('even2', background='#EEEEEE',
                           font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('odd3', font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('even3', background='#DDDDDD',
                           font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('red', foreground='#ff0089',
                           font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('green', foreground='#008B8B',
                           font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('black', font=tkfont.nametofont('TkTextFont'))
        tree.pack(fill='both', padx=5, pady=5, ipadx=2, ipady=2)
        BtnFm = tk.Frame(ResTable)
        BtnFm.pack(side=tk.TOP, padx=6, pady=6)
        bull_btn = ttk.Button(BtnFm, text='多單進出場點位',
                              command=lambda: Annotate(ResTable, bull_name))
        bull_btn.pack(side=tk.LEFT, padx=80, pady=6, ipadx=4, ipady=4)
        bear_btn = ttk.Button(BtnFm, text='空單進出場點位',
                              command=lambda: Annotate(ResTable, bear_name))
        bear_btn.pack(side=tk.RIGHT, padx=80, pady=6, ipadx=4, ipady=4)
    elif not bull_exist and bear_exist:
        messagebox.showwarning('策略回測', '未篩選出任何多單標的，請重新設定參數')
    elif bull_exist and not bear_exist:
        messagebox.showwarning('策略回測', '未篩選出任何空單標的，請重新設定參數')
    else:
        messagebox.showwarning('策略回測', '未篩選出任何多單及空單標的，請重新設定參數')


def ExeBacktest(Bullin, Bullout, Bearin, Bearout, BullSL, BullTP, BearSL, BearTP, min_cap, max_cap, root01, root02, bull_opt_lt, bullout_opt_lt, bear_opt_lt, bearout_opt_lt, MonAmt, select_priority, group_dict):
    exe_lt = []
    select_priority, group_dict = {skey: sval.get() for skey, sval in select_priority.items()}, {
        gkey: gval.get() for gkey, gval in group_dict.items()}
    value_lt, principle_dict = [BullSL, BullTP, BearSL, BearTP, group_dict['多單最低報酬率'],
                                group_dict['空單最低報酬率']], {'多單本金': group_dict['多單本金'], '空單本金': group_dict['空單本金']}
    cap_lt = [min_cap, max_cap]
    try:
        for i in range(len(value_lt)):
            value_lt[i] = float(value_lt[i])
            value_lt[i] /= 100
        for i in range(len(cap_lt)):
            cap_lt[i] = float(cap_lt[i])
        for k in principle_dict.keys():
            principle_dict[k] = float(principle_dict[k]) * 10000
            if principle_dict[k] < 10000:
                messagebox.showwarning('策略回測', '本金不能小於10000元')
        for group_k in group_dict.keys():
            group_dict[group_k] = float(group_dict[group_k])
            if '最低報酬率' in group_k:
                group_dict[group_k] = group_dict[group_k] * 0.01
            elif '最低現金' in group_k:
                group_dict[group_k] = group_dict[group_k] * 10000
            if group_dict[group_k] < 0:
                messagebox.showwarning('策略回測', '所有數值皆須大於0')
                raise IndexError
    except Exception as err:
        print(err)
        backtest_msg('number')
    else:
        if (Bullin == strategy_lt[0] and Bearin == strategy_lt[0]) or (Bullin != strategy_lt[0] and Bullout == strategy_lt[0]) or (Bearin != strategy_lt[0] and Bearout == strategy_lt[0]) or (Bullin == strategy_lt[0] and Bullout != strategy_lt[0]) or (Bearin == strategy_lt[0] and Bearout != strategy_lt[0]):
            backtest_msg('cond')
        elif value_lt[0] <= 0 or value_lt[1] <= 0 or value_lt[2] <= 0 or value_lt[3] <= 0:
            backtest_msg('value')
        elif cap_lt[0] < 0 or cap_lt[1] < 0:
            backtest_msg('cap')
        elif cap_lt[0] >= cap_lt[1]:
            backtest_msg('seq')
        elif group_dict['多單最低現金'] + group_dict['多單金額上限'] > principle_dict['多單本金'] or group_dict['空單最低現金'] + group_dict['空單金額上限'] > principle_dict['空單本金']:
            messagebox.showwarning('策略回測', '每筆交易金額上限與最低現金餘額的總和\n不能大於本金')
        else:
            BullTradeExist,  BearTradeExist = False, False
            if cap_lt[0] != 0 or cap_lt[1] != 200:
                if cap_lt[0] == 0 and cap_lt[1] >= 2593.04:
                    with open('D:/stocks/below200.txt', newline='\n', encoding='utf-8') as b200:
                        lastb200 = list(csv.reader(b200))[-1][0]
                    last_cd_idx = code_lt.index(lastb200)
                    for c_num, cd in enumerate(code_lt):
                        if c_num <= last_cd_idx:
                            exe_lt.append(cd)
                else:
                    exe_lt = select_stk(cap_lt[0], cap_lt[1])
                if '1000' in exe_lt:
                    exe_lt.remove('1000')
            else:
                with open('D:/stocks/below200.txt', newline='\n', encoding='utf-8') as b200:
                    reader = list(csv.reader(b200))
                    for row in reader:
                        exe_lt.append(row[0])
            bull_in_idx = strategy_lt.index(Bullin)
            bull_out_idx = strategy_lt.index(Bullout)
            bull_in_name = '0' + \
                str(bull_in_idx) if bull_in_idx < 10 else str(bull_in_idx)
            bull_out_name = '0' + \
                str(bull_out_idx) if bull_out_idx < 10 else str(bull_out_idx)
            bull_rec_name = 'D:/2016_2019/backtest/b' + \
                bull_in_name + bull_out_name + '-' + time_now + '.csv'
            bear_in_idx = strategy_lt.index(Bearin)
            bear_out_idx = strategy_lt.index(Bearout)
            bear_in_name = '0' + \
                str(bear_in_idx) if bear_in_idx < 10 else str(bear_in_idx)
            bear_out_name = '0' + \
                str(bear_out_idx) if bear_out_idx < 10 else str(bear_out_idx)
            bear_rec_name = 'D:/2016_2019/backtest/s' + \
                bear_in_name + bear_out_name + '-' + time_now + '.csv'
            bull_rec_dict, inout, bull_opts = {'name': 'b' + bull_in_name + bull_out_name + '-' + time_now + '.csv',
                                               'sl': value_lt[0], 'tp': value_lt[1], 'principle': principle_dict['多單本金'],
                                               'mincap': min_cap, 'maxcap': max_cap, 'monamt': MonAmt, 'priority': select_dict[select_priority['多單篩選依據']],
                                               'seq': 'ascend' if select_priority['多單排序'] == '由低到高' else 'descend', 'mincp': group_dict['多單最低報酬率'], 'uplimit': group_dict['多單金額上限'],
                                               'mincash': group_dict['多單最低現金'], 'invest': group_dict['多單投入金額']}, ('in', 'out'), (bull_opt_lt, bullout_opt_lt)
            for opt_group in bull_opts:
                for vnum, val in enumerate(opt_group):
                    bull_rec_dict[inout[bull_opts.index(
                        opt_group)] + str(vnum)] = val
            bear_rec_dict, bear_opts = {'name': 's' + bear_in_name + bear_out_name + '-' + time_now + '.csv',
                                        'sl': value_lt[2], 'tp': value_lt[3], 'principle': principle_dict['空單本金'],
                                        'mincap': min_cap, 'maxcap': max_cap, 'monamt': MonAmt, 'priority': select_dict[select_priority['空單篩選依據']],
                                        'seq': 'ascend' if select_priority['空單排序'] == '由低到高' else 'descend', 'mincp': group_dict['空單最低報酬率'], 'uplimit': group_dict['空單金額上限'],
                                        'mincash': group_dict['空單最低現金'], 'invest': group_dict['空單投入金額']}, (bear_opt_lt, bearout_opt_lt)
            for opt_group in bear_opts:
                for vnum, val in enumerate(opt_group):
                    bear_rec_dict[inout[bear_opts.index(
                        opt_group)] + str(vnum)] = val
            for rec_dict in (bull_rec_dict, bear_rec_dict):
                rec_df = pd.DataFrame(rec_dict, index=[0])
                pre_df = pd.read_csv('D:/stocks/Rec.csv')
                pre_df = pre_df.append(rec_df, ignore_index=True, sort=False)
                pre_df.to_csv('D:/stocks/Rec.csv',
                              index=False, encoding='utf-8')
            done_lt = []
            root01.destroy()
            root02.destroy()
            if Bullin != '無':
                with open(bull_rec_name, 'a', newline='\n',
                          encoding='utf-8') as f:
                    wr = csv.writer(f)
                    wr.writerow(bull_columns)
                bull_trade_df = pd.read_csv(bull_rec_name, parse_dates=[
                    'buy_date', 'sell_date'])
                for product in exe_lt:
                    print('Start:', product)
                    bullin_df = opt_dict.get(Bullin)(product, 'BullIn', value_lt[0], value_lt[1], value_lt[2], value_lt[3], [], [
                    ], bull_opt_lt[0], bull_opt_lt[1], bull_opt_lt[2], bull_opt_lt[3], bull_opt_lt[4], bull_opt_lt[5], MonAmt, value_lt[4], 'backtest')
                    if len(bullin_df) != 0:
                        bullout_df = opt_dict.get(Bullout)(product, 'BullOut', value_lt[0], value_lt[1], value_lt[2], value_lt[3], bullin_df, [
                        ], bullout_opt_lt[0], bullout_opt_lt[1], bullout_opt_lt[2], bullout_opt_lt[3], bullout_opt_lt[4], bullout_opt_lt[5], MonAmt, value_lt[4], 'backtest')
                        drop_lt = []
                        for x in range(len(bullout_df)):
                            if bullout_df.loc[x, 'sell_p'] == 0:
                                drop_lt.append(x)
                        if drop_lt != []:
                            bullout_df.drop(index=drop_lt, inplace=True)
                        bull_trade_df = bull_trade_df.append(
                            bullout_df, ignore_index=True, sort=False)
                        bull_trade_df = bull_trade_df.astype(
                            {'code': 'int16', 'sell_date': 'datetime64'})
                        print(
                            product, name_lt[code_lt.index(product)], '有多單進場')
                        BullTradeExist = True
                bull_trade_df.to_csv(bull_rec_name, index=False)
            if Bearin != '無':
                with open(bear_rec_name, 'a', newline='\n',
                          encoding='utf-8') as f:
                    wr = csv.writer(f)
                    wr.writerow(bear_col_lt)
                bear_trade_df = pd.read_csv(bear_rec_name, parse_dates=[
                    'sell_date', 'buy_date'])
                for product in exe_lt:
                    print('Start:', product)
                    bearin_df = opt_dict.get(Bearin)(product, 'BearIn', value_lt[0], value_lt[1], value_lt[2], value_lt[3], [], [
                    ], bear_opt_lt[0], bear_opt_lt[1], bear_opt_lt[2], bear_opt_lt[3], bear_opt_lt[4], bear_opt_lt[5], MonAmt, value_lt[5], 'backtest')
                    if len(bearin_df) != 0:
                        bearout_df = opt_dict.get(Bearout)(product, 'BearOut', value_lt[0], value_lt[1], value_lt[2], value_lt[3], [
                        ], bearin_df, bearout_opt_lt[0], bearout_opt_lt[1], bearout_opt_lt[2], bearout_opt_lt[3], bearout_opt_lt[4], bearout_opt_lt[5], MonAmt, value_lt[5], 'backtest')
                        drop_lt = []
                        for x in range(len(bearout_df)):
                            if bearout_df.loc[x, 'buy_p'] == 0:
                                drop_lt.append(x)
                        if drop_lt != []:
                            bearout_df.drop(index=drop_lt, inplace=True)
                        bear_trade_df = bear_trade_df.append(
                            bearout_df, ignore_index=True, sort=False)
                        bear_trade_df = bear_trade_df.astype(
                            {'code': 'int16', 'buy_date': 'datetime64'})
                        print(
                            product, name_lt[code_lt.index(product)], '有空單進場')
                        BearTradeExist = True
                bear_trade_df.to_csv(bear_rec_name, index=False)
            if not BullTradeExist and not BearTradeExist:
                messagebox.showinfo('策略回測', '沒有股票符合你的多單及空單條件')
            elif BullTradeExist and not BearTradeExist:
                messagebox.showinfo('策略回測', '沒有股票符合你的空單條件')
            elif not BullTradeExist and BearTradeExist:
                messagebox.showinfo('策略回測', '沒有股票符合你的多單條件')
            else:
                exist_lt = {bull_rec_name: BullTradeExist,
                            bear_rec_name: BearTradeExist}
                for rec in exist_lt:
                    rec_df = pd.read_csv(
                        rec, parse_dates=['buy_date', 'sell_date'])
                    if exist_lt[rec] and rec == bull_rec_name:
                        rec_df['cp'] = (
                            rec_df['sell_p'] * (1 - fee - tax)) / (rec_df['buy_p'] * (fee + 1)) - 1
                        rec_df['win'] = np.where(rec_df['cp'] > 0, 1, 0)
                        rec_df.to_csv('D:/2016_2019/rawbacktest/' +
                                      bull_rec_name[22:], index=False)
                        rec_df['days'] = rec_df['sell_date'] - \
                            rec_df['buy_date']
                        rec_df['days'] = rec_df['days'].apply(
                            lambda x: int(str(x).split(' ')[0]))
                        rec_df['chg_amt'] = rec_df['sell_p'] * \
                            (1 - fee - tax) - rec_df['buy_p'] * (fee + 1)
                        rec_df['ar'] = pow(
                            1 + rec_df['cp'], 240 / rec_df['days']) - 1
                        rec_df.sort_values(
                            by=['buy_date', 'sell_date'], inplace=True)
                        rec_df.to_csv(bull_rec_name, index=False)
                    if exist_lt[rec] and rec == bear_rec_name:
                        rec_df['cp'] = (
                            rec_df['sell_p'] * (1 - margin * (fee + tax))) / (rec_df['buy_p'] * (fee + 1)) - 1
                        rec_df['win'] = np.where(rec_df['cp'] > 0, 1, 0)
                        rec_df.to_csv('D:/2016_2019/rawbacktest/' +
                                      bear_rec_name[22:], index=False)
                        rec_df['days'] = rec_df['buy_date'] - \
                            rec_df['sell_date']
                        rec_df['days'] = rec_df['days'].apply(
                            lambda x: int(str(x).split(' ')[0]))
                        rec_df['chg_amt'] = rec_df['sell_p'] * \
                            (1 - margin * (fee + tax)) - \
                            rec_df['buy_p'] * (fee + 1)
                        rec_df['ar'] = pow(
                            1 + rec_df['cp'], 240 / rec_df['days']) - 1
                        rec_df.sort_values(
                            by=['sell_date', 'buy_date'], inplace=True)
                        rec_df.to_csv(bear_rec_name, index=False)
                ShowResult(bull_rec_name, bear_rec_name, BullTradeExist,
                           BearTradeExist, principle_dict, select_priority, group_dict, 'done')


def BacktestPage(window):
    window.wm_state('iconic')

    def destroy_win(root1, root2):
        root1.destroy()
        root2.destroy()

    def click_enter01(self):
        SetParameter(BacktestWin, [comBullin.get(
        ), comBullout.get(), comBearin.get(), comBearout.get()])

    def SetParameter(root, option_list):
        def click_start(self):
            ExeBacktest(comBullin.get(), comBullout.get(), comBearin.get(),
                        comBearout.get(), comBullSL.get(), comBullTP.get(),
                        comBearSL.get(), comBearTP.get(), comCapMin.get(),
                        comCapMax.get(), ValWin, root,
                        [float(obj.get()) for obj in option_tup[:6]],
                        [float(obj.get()) for obj in option_tup[6:12]],
                        [float(obj.get()) for obj in option_tup[12:18]],
                        [float(obj.get()) for obj in option_tup[18:]], float(comVol.get()), select_priority, group_dict)
        ValWin = tk.Toplevel()
        root.wm_state('iconic')
        ValWin.title('策略回測')
        ValWin.geometry('630x525+50+0')
        ValWin.iconbitmap('D:/stocks/stock.ico')
        Group02 = tk.LabelFrame(ValWin, padx=4, pady=4)
        Group02.grid(row=0, column=0, columnspan=2, padx=4,
                     pady=4, ipadx=2, ipady=2, sticky='news')
        tk.Label(Group02, text='多單進場參數').grid(
            row=0, column=0, padx=5, pady=5, ipadx=2, ipady=2)
        comBullOpt01 = ttk.Combobox(
            Group02, width=5, values=[0.05, 0.04, 0.03])
        comBullOpt01.grid(row=0, column=1, padx=5, pady=5, ipadx=2, ipady=2)
        comBullOpt02 = ttk.Combobox(Group02, width=5, values=[
            0.06, 0.07, 0.08, 0.09, 0.1])
        comBullOpt02.grid(row=0, column=2, padx=5, pady=5, ipadx=2, ipady=2)
        comBullOpt03 = ttk.Combobox(
            Group02, width=5, values=[0.01, 0.02, 0.03])
        comBullOpt03.grid(row=0, column=3, padx=5, pady=5, ipadx=2, ipady=2)
        comBullOpt04 = ttk.Combobox(Group02, width=5, values=[0.8, 1])
        comBullOpt04.grid(row=0, column=4, padx=5, pady=5, ipadx=2, ipady=2)
        comBullOpt05 = ttk.Combobox(Group02, width=5, values=[2, 1.5, 1])
        comBullOpt05.grid(row=0, column=5, padx=5, pady=5, ipadx=2, ipady=2)
        comBullOpt06 = ttk.Combobox(Group02, width=5, values=[0.5, 1, 1.5, 2])
        comBullOpt06.grid(row=0, column=6, padx=5, pady=5, ipadx=2, ipady=2)
        tk.Label(Group02, text='多單出場參數').grid(
            row=1, column=0, padx=5, pady=5, ipadx=2, ipady=2)
        comBulloutOpt01 = ttk.Combobox(Group02, width=5, values=[-0.01])
        comBulloutOpt01.grid(row=1, column=1, padx=5, pady=5, ipadx=2, ipady=2)
        comBulloutOpt02 = ttk.Combobox(Group02, width=5, values=[0.6, 0.7])
        comBulloutOpt02.grid(row=1, column=2, padx=5, pady=5, ipadx=2, ipady=2)
        comBulloutOpt03 = ttk.Combobox(Group02, width=5, values=[0, -0.01])
        comBulloutOpt03.grid(row=1, column=3, padx=5, pady=5, ipadx=2, ipady=2)
        comBulloutOpt04 = ttk.Combobox(Group02, width=5, values=[1, 1.5])
        comBulloutOpt04.grid(row=1, column=4, padx=5, pady=5, ipadx=2, ipady=2)
        comBulloutOpt05 = ttk.Combobox(Group02, width=5, values=[-1, 0])
        comBulloutOpt05.grid(row=1, column=5, padx=5, pady=5, ipadx=2, ipady=2)
        comBulloutOpt06 = ttk.Combobox(Group02, width=5, values=[0.08])
        comBulloutOpt06.grid(row=1, column=6, padx=5, pady=5, ipadx=2, ipady=2)
        tk.Label(Group02, text='空單進場參數').grid(
            row=2, column=0, padx=5, pady=5, ipadx=2, ipady=2)
        comBearOpt01 = ttk.Combobox(Group02, width=5, values=[2])
        comBearOpt01.grid(row=2, column=1, padx=5, pady=5, ipadx=2, ipady=2)
        comBearOpt02 = ttk.Combobox(Group02, width=5, values=[0.08, 0.1])
        comBearOpt02.grid(row=2, column=2, padx=5, pady=5, ipadx=2, ipady=2)
        comBearOpt03 = ttk.Combobox(Group02, width=5, values=[0.08, 0.1])
        comBearOpt03.grid(row=2, column=3, padx=5, pady=5, ipadx=2, ipady=2)
        comBearOpt04 = ttk.Combobox(
            Group02, width=5, values=[-0.005, -0.001, 0])
        comBearOpt04.grid(row=2, column=4, padx=5, pady=5, ipadx=2, ipady=2)
        comBearOpt05 = ttk.Combobox(Group02, width=5, values=[0.05])
        comBearOpt05.grid(row=2, column=5, padx=5, pady=5, ipadx=2, ipady=2)
        comBearOpt06 = ttk.Combobox(Group02, width=5, values=[0.08, 0.1])
        comBearOpt06.grid(row=2, column=6, padx=5, pady=5, ipadx=2, ipady=2)
        tk.Label(Group02, text='空單出場參數').grid(
            row=3, column=0, padx=5, pady=5, ipadx=2, ipady=2)
        comBearoutOpt01 = ttk.Combobox(Group02, width=5, values=[2])
        comBearoutOpt01.grid(row=3, column=1, padx=5, pady=5, ipadx=2, ipady=2)
        comBearoutOpt02 = ttk.Combobox(Group02, width=5, values=[0.08])
        comBearoutOpt02.grid(row=3, column=2, padx=5, pady=5, ipadx=2, ipady=2)
        comBearoutOpt03 = ttk.Combobox(Group02, width=5, values=[0.08])
        comBearoutOpt03.grid(row=3, column=3, padx=5, pady=5, ipadx=2, ipady=2)
        comBearoutOpt04 = ttk.Combobox(Group02, width=5, values=[0])
        comBearoutOpt04.grid(row=3, column=4, padx=5, pady=5, ipadx=2, ipady=2)
        comBearoutOpt05 = ttk.Combobox(Group02, width=5, values=[0.05])
        comBearoutOpt05.grid(row=3, column=5, padx=5, pady=5, ipadx=2, ipady=2)
        comBearoutOpt06 = ttk.Combobox(Group02, width=5, values=[0.08])
        comBearoutOpt06.grid(row=3, column=6, padx=5, pady=5, ipadx=2, ipady=2)
        GroupBull = tk.LabelFrame(ValWin, text='多單', padx=0, pady=0)
        GroupBull.grid(row=1, column=0, padx=4, pady=4,
                       ipadx=2, ipady=2, sticky='news')
        GroupBear = tk.LabelFrame(ValWin, text='空單', padx=0, pady=0)
        GroupBear.grid(row=1, column=1, padx=4, pady=4,
                       ipadx=2, ipady=2, sticky='news')
        group_name_dict, group_dict = {'多單': GroupBull, '空單': GroupBear}, {}
        for TextKey, Group in group_name_dict.items():
            MincpLabel = tk.Label(Group, text='最低預期報酬率(%)')
            MincpLabel.grid(row=0, column=0, padx=5, pady=5, ipadx=2, ipady=2)
            comMincp = ttk.Combobox(Group, width=8, values=[3, 4, 5])
            comMincp.grid(row=0, column=1, padx=5, pady=5, ipadx=2, ipady=2)
            comMincp.current(0)
            group_dict[TextKey + '最低報酬率'] = comMincp
            tk.Label(Group, text='初始本金(萬元)').grid(
                row=1, column=0, padx=5, pady=5, ipadx=2, ipady=2)
            comMoney = ttk.Combobox(Group, width=8, values=[100, 500])
            comMoney.grid(row=1, column=1, padx=5, pady=5, ipadx=2, ipady=2)
            comMoney.current(0)
            group_dict[TextKey + '本金'] = comMoney
            tk.Label(Group, text='每筆交易金額上限(元)').grid(
                row=2, column=0, padx=5, pady=5, ipadx=2, ipady=2)
            comUplimit = ttk.Combobox(Group, width=8, values=[
                prop for prop in range(10000, 50100, 100)])
            comUplimit.grid(row=2, column=1, padx=5, pady=5, ipadx=2, ipady=2)
            comUplimit.current(50)
            group_dict[TextKey + '金額上限'] = comUplimit
            tk.Label(Group, text='最低現金餘額(萬)').grid(
                row=3, column=0, padx=5, pady=5, ipadx=2, ipady=2)
            comMinCash = ttk.Combobox(Group, width=8, values=[
                prop for prop in range(10, 21)])
            comMinCash.grid(row=3, column=1, padx=5, pady=5, ipadx=2, ipady=2)
            comMinCash.current(0)
            group_dict[TextKey + '最低現金'] = comMinCash
            tk.Label(Group, text='每月投入金額(元)').grid(
                row=4, column=0, padx=5, pady=5, ipadx=2, ipady=2)
            comInvest = ttk.Combobox(Group, width=8, values=[5000, 10000])
            comInvest.grid(row=4, column=1, padx=5, pady=5, ipadx=2, ipady=2)
            comInvest.current(0)
            group_dict[TextKey + '投入金額'] = comInvest
        Group03 = tk.LabelFrame(ValWin, padx=4, pady=4)
        Group03.grid(row=2, column=0, columnspan=2, padx=4,
                     pady=4, ipadx=2, ipady=2, sticky='news')
        select_priority, dir_tup = {}, ('多單篩選依據', '空單篩選依據')
        for enum, textLabel in enumerate(dir_tup):
            tk.Label(Group03, text=textLabel).grid(
                row=enum, column=0, padx=4, pady=4, ipadx=2, ipady=2)
            comPriority = ttk.Combobox(
                Group03, width=15, values=tuple(select_dict), state='readonly')
            comPriority.grid(row=enum, column=1, padx=4,
                             pady=4, ipadx=2, ipady=2)
            select_priority[textLabel] = comPriority
            comPriority.current(0)
            comSeq = ttk.Combobox(Group03, width=8, values=(
                '由高到低', '由低到高'), state='readonly')
            comSeq.grid(row=enum, column=2, padx=4, pady=4, ipadx=2, ipady=2)
            select_priority[textLabel[:2] + '排序'] = comSeq
            comSeq.current(0)
        option_tup = (comBullOpt01, comBullOpt02, comBullOpt03, comBullOpt04, comBullOpt05, comBullOpt06,
                      comBulloutOpt01, comBulloutOpt02, comBulloutOpt03, comBulloutOpt04, comBulloutOpt05, comBulloutOpt06,
                      comBearOpt01, comBearOpt02, comBearOpt03, comBearOpt04, comBearOpt05, comBearOpt06,
                      comBearoutOpt01, comBearoutOpt02, comBearoutOpt03, comBearoutOpt04, comBearoutOpt05, comBearoutOpt06)
        with open('D:/stocks/parameter.txt', newline='\n', encoding='utf-8') as pf:
            p_list, p_dict = list(csv.reader(pf)), {}
            for line in p_list:
                p_dict[line[0]] = line[1:]
            for seq, opt_name in enumerate(option_list):
                if opt_name in p_dict:
                    val_tup = option_tup[seq * 6:seq * 6 + 6]
                    for e, opt in enumerate(val_tup):
                        opt.set(p_dict[opt_name][e])

        try:
            StartBtn = ttk.Button(Group03, width=6, text='確定', command=lambda: ExeBacktest(comBullin.get(), comBullout.get(), comBearin.get(),
                                                                                           comBearout.get(), comBullSL.get(), comBullTP.get(),
                                                                                           comBearSL.get(), comBearTP.get(), comCapMin.get(),
                                                                                           comCapMax.get(), ValWin, root,
                                                                                           [float(
                                                                                               obj.get()) for obj in option_tup[:6]],
                                                                                           [float(
                                                                                               obj.get()) for obj in option_tup[6:12]],
                                                                                           [float(
                                                                                               obj.get()) for obj in option_tup[12:18]],
                                                                                           [float(obj.get()) for obj in option_tup[18:]], float(comVol.get()), select_priority, group_dict))
            tk.Label(Group03, text='    ').grid(row=0, column=3,
                                                rowspan=2, padx=4, pady=4, ipadx=2, ipady=2)
            StartBtn.grid(row=0, column=4, rowspan=2,
                          padx=4, pady=4, ipadx=2, ipady=2)
            ttk.Button(Group03, width=6, text='取消', command=lambda: destroy_win(
                ValWin, root)).grid(row=0, column=5, rowspan=2,  padx=4, pady=4, ipadx=2, ipady=2)
            # ttk.Button(Group03, width = 6, text = '返回', command = lambda: root.wm_state('normal')).grid(row = 0, column = 5, rowspan = 2,  padx = 4, pady = 4, ipadx = 2, ipady = 2)
            ValWin.bind('<Return>', click_start)
        except Exception as err:
            print('Error:', err)
            backtest_msg('option')
    BacktestWin = tk.Toplevel()
    BacktestWin.title('策略回測')
    BacktestWin.geometry('700x290+50+0')
    BacktestWin.iconbitmap('D:/stocks/stock.ico')
    BacktestWin.lift()
    Group01 = tk.LabelFrame(BacktestWin, padx=4, pady=4)
    Group01.pack(fill='x', padx=12, pady=12, ipadx=4, ipady=4)
    BullinLabel = tk.Label(Group01, text='多單進場策略')
    BullinLabel.grid(row=0, column=0, padx=5, pady=5, ipadx=2, ipady=2)

    comBullin = ttk.Combobox(
        Group01, width=12, values=strategy_lt, state='readonly')
    comBullin.grid(row=0, column=1, padx=5, pady=5, ipadx=2, ipady=2)
    comBullin.current(2)
    blankLabel01 = tk.Label(Group01, text='')
    blankLabel01.grid(row=1, column=0)

    BulloutLabel = tk.Label(Group01, text='多單出場策略')
    BulloutLabel.grid(row=2, column=0, padx=5, pady=5, ipadx=2, ipady=2)

    comBullout = ttk.Combobox(
        Group01, width=12, values=strategy_lt, state='readonly')
    comBullout.grid(row=2, column=1, padx=5, pady=5, ipadx=2, ipady=2)
    comBullout.current(3)
    blankLabel03 = tk.Label(Group01, text='')
    blankLabel03.grid(row=3, column=0)

    BearinLabel = tk.Label(Group01, text='空單進場策略')
    BearinLabel.grid(row=4, column=0, padx=5, pady=5, ipadx=2, ipady=2)

    comBearin = ttk.Combobox(
        Group01, width=12, values=strategy_lt, state='readonly')
    comBearin.grid(row=4, column=1, padx=5, pady=5, ipadx=2, ipady=2)
    comBearin.current(3)
    blankLabel05 = tk.Label(Group01, text='')
    blankLabel05.grid(row=5, column=0)

    BearoutLabel = tk.Label(Group01, text='空單出場策略')
    BearoutLabel.grid(row=6, column=0, padx=5, pady=5, ipadx=2, ipady=2)

    comBearout = ttk.Combobox(
        Group01, width=12, values=strategy_lt, state='readonly')
    comBearout.grid(row=6, column=1, padx=5, pady=5, ipadx=2, ipady=2)
    comBearout.current(1)

    blankLabel_cross0 = tk.Label(Group01, text='   ')
    blankLabel_cross0.grid(row=0, column=3)

    BullStopLossLabel = tk.Label(Group01, text='多單停損')
    BullStopLossLabel.grid(row=0, column=4, padx=5, pady=5, ipadx=2, ipady=2)

    comBullSL = ttk.Combobox(Group01, width=5, values=pct_lt)
    comBullSL.grid(row=0, column=5, padx=5, pady=5, ipadx=2, ipady=2)
    comBullSL.current(4)
    BullStopLossLabel2 = tk.Label(Group01, text='%')
    BullStopLossLabel2.grid(row=0, column=6)

    blankLabel_cross0_0 = tk.Label(Group01, text='')
    blankLabel_cross0_0.grid(row=0, column=7)
    CapMinLabel = tk.Label(Group01, text='股本(億元)≥')
    CapMinLabel.grid(row=0, column=8)
    comCapMin = ttk.Combobox(Group01, width=5, values=[0, 10])
    comCapMin.grid(row=0, column=9, padx=5, pady=5, ipadx=2, ipady=2)
    comCapMin.current(0)

    blankLabel_cross2 = tk.Label(Group01, text='   ')
    blankLabel_cross2.grid(row=2, column=3)

    BullTakeProfitLabel = tk.Label(Group01, text='多單停利')
    BullTakeProfitLabel.grid(row=2, column=4, padx=5, pady=5, ipadx=2, ipady=2)

    comBullTP = ttk.Combobox(Group01, width=5, values=pct_lt)
    comBullTP.grid(row=2, column=5, padx=5, pady=5, ipadx=2, ipady=2)
    comBullTP.current(4)
    BullTakeProfitLabel2 = tk.Label(Group01, text='%')
    BullTakeProfitLabel2.grid(row=2, column=6)

    blankLabel_cross4 = tk.Label(Group01, text='   ')
    blankLabel_cross4.grid(row=4, column=3)

    BearStopLossLabel = tk.Label(Group01, text='空單停損')
    BearStopLossLabel.grid(row=4, column=4, padx=5, pady=5, ipadx=2, ipady=2)

    comBearSL = ttk.Combobox(Group01, width=5, values=pct_lt)
    comBearSL.grid(row=4, column=5, padx=5, pady=5, ipadx=2, ipady=2)
    comBearSL.current(3)
    BearStopLossLabel2 = tk.Label(Group01, text='%')
    BearStopLossLabel2.grid(row=4, column=6)

    blankLabel_cross6 = tk.Label(Group01, text='   ')
    blankLabel_cross6.grid(row=6, column=3)

    BearTakeProfitLabel = tk.Label(Group01, text='空單停利')
    BearTakeProfitLabel.grid(row=6, column=4, padx=5, pady=5, ipadx=2, ipady=2)

    comBearTP = ttk.Combobox(Group01, width=5, values=pct_lt)
    comBearTP.grid(row=6, column=5, padx=5, pady=5, ipadx=2, ipady=2)
    comBearTP.current(3)
    BearTakeProfitLabel2 = tk.Label(Group01, text='%')
    BearTakeProfitLabel2.grid(row=6, column=6)

    blankLabel_cross2_2 = tk.Label(Group01, text='   ')
    blankLabel_cross2_2.grid(row=2, column=7)
    CapMaxLabel = tk.Label(Group01, text='股本(億元)≤')
    CapMaxLabel.grid(row=2, column=8, padx=5, pady=5, ipadx=2, ipady=2)
    comCapMax = ttk.Combobox(Group01, width=5, values=[200, 500])
    comCapMax.grid(row=2, column=9, padx=5, pady=5, ipadx=2, ipady=2)
    comCapMax.current(0)
    comVol = ttk.Combobox(Group01, width=5, values=[50000, 100000])
    comVol.grid(row=4, column=9, padx=5, pady=5, ipadx=2, ipady=2)
    comVol.current(0)
    VolLabel = tk.Label(Group01, text='月均量(仟元)≥')
    VolLabel.grid(row=4, column=8, padx=5, pady=5, ipadx=2, ipady=2)
    ttk.Button(Group01, text='繼續', command=lambda: SetParameter(BacktestWin, [comBullin.get(), comBullout.get(
    ), comBearin.get(), comBearout.get()])).grid(row=6, column=8, columnspan=2, padx=5, pady=5, ipadx=2, ipady=2)
    BacktestWin.bind('<Return>', click_enter01)


def SearchPage(chk_lt, plot_lt, file):
    def info_msg(input_str, warn_label, msg_label):
        if len(input_str) > 2 and (input_str[-1] == 'y' or input_str[-2] == 'k'):
            true_str = input_str[:-2] + 'KY'
        else:
            true_str = input_str
        if true_str not in code_lt and true_str not in name_lt:
            warn_label.config(text=true_str)
            msg_label.config(text='不存在')
        else:
            if true_str in code_lt:
                stk_name, code = name_lt[code_lt.index(true_str)], true_str
                msg_label.config(text=stk_name + '（' + true_str + '）')
            else:
                code = code_lt[name_lt.index(true_str)]
                msg_label.config(text=true_str + '（' + code + '）')
            warn_label.config(text='個股：')
            record = ShowAnnotation(code, file, chk_lt, plot_lt)
            if file != 0 and record == 1:
                backtest_msg('no record')

    def click_enter(self):
        info_msg(str(CodeString.get()), warn_label, msg_label)
    SearchWin = tk.Toplevel()
    SearchWin.geometry('328x63+307+200')
    SearchWin.iconbitmap('D:/stocks/stock.ico')
    CodeString = tk.StringVar()
    entry_label = tk.Label(SearchWin, text=' 輸入代碼/名稱 ')
    entry_label.grid(row=0, column=0)
    entry_win = ttk.Entry(SearchWin, width=8, textvariable=CodeString)
    entry_win.grid(row=0, column=1)
    warn_label = tk.Label(SearchWin, text='')
    warn_label.grid(row=1, column=0)
    msg_label = tk.Label(SearchWin, text='')
    msg_label.grid(row=1, column=1)
    entry_btn = ttk.Button(SearchWin, text='查詢', command=lambda: info_msg(
        str(CodeString.get()), warn_label, msg_label))
    entry_btn.grid(row=0, column=2)
    entry_win.bind("<Return>", click_enter)


def Choose(root):
    def send_strategy(bull_name, bear_name, root):
        if len(bull_name) != 0 and len(bear_name) != 0:
            root.destroy()
            sharehold_files = listdir('D:/2016_2019/shareholding/')
            with open('D:/stocks/tdy_done.txt', newline='\n', encoding='utf-8') as tdydone_list:
                last_tdy_done = list(csv.reader(tdydone_list))[-1][0]
            with open('D:/stocks/select_done.txt', newline='\n', encoding='utf-8') as select_list:
                s_done_lt = list(csv.reader(select_list))
            if (bull_name in sharehold_files and [bull_name, last_tdy_done] not in s_done_lt) or bull_name not in sharehold_files:
                print('Select stocks for bull trend')
                select(bull_name)
            if (bear_name in sharehold_files and [bear_name, last_tdy_done] not in s_done_lt) or bear_name not in sharehold_files:
                print('Select stocks for bear trend')
                select(bear_name)
            SWin = tk.Toplevel()
            SWin.geometry('388x100+307+200')
            SWin.title('篩選結果')
            SWin.iconbitmap('D:/stocks/stock.ico')
            bullin_btn = ttk.Button(
                SWin, text='多單進場訊號', command=lambda: show_select_result(0, 'in', '多單進場訊號'))
            bullin_btn.grid(row=0, column=0, padx=8, pady=8, ipadx=2, ipady=2)
            bearin_btn = ttk.Button(
                SWin, text='空單進場訊號', command=lambda: show_select_result(1, 'in', '空單進場訊號'))
            bearin_btn.grid(row=1, column=0, padx=8, pady=8, ipadx=2, ipady=2)
            bullout_btn = ttk.Button(
                SWin, text='多單出場訊號', command=lambda: show_select_result(0, 'out', '多單出場訊號'))
            bullout_btn.grid(row=0, column=1, padx=8, pady=8, ipadx=2, ipady=2)
            bearout_btn = ttk.Button(
                SWin, text='空單出場訊號', command=lambda: show_select_result(1, 'out', '空單出場訊號'))
            bearout_btn.grid(row=1, column=1, padx=8, pady=8, ipadx=2, ipady=2)
            ttk.Button(SWin, text='多單詳細資料', command=lambda: show_select_result(0, 'inout', '多單詳細資料')).grid(row=0,
                                                                                                           column=2, padx=8, pady=8, ipadx=2, ipady=2)
            ttk.Button(SWin, text='空單詳細資料', command=lambda: show_select_result(1, 'inout', '空單詳細資料')).grid(row=1,
                                                                                                           column=2, padx=8, pady=8, ipadx=2, ipady=2)

            def selectItem(item_dict, focus):
                try:
                    cur_code = str(item_dict['values'][0])
                    import webbrowser
                    webbrowser.open_new_tab(
                        'https://histock.tw/stock/' + cur_code)
                except Exception as err:
                    print(err)
                    print('無法開啟指定網頁')

            def show_select_result(df_idx, in_or_out, Title):
                bull_df = pd.read_csv(
                    'D:/2016_2019/shareholding/' + bull_name, parse_dates=['buy_date', 'sell_date'])
                bear_df = pd.read_csv(
                    'D:/2016_2019/shareholding/' + bear_name, parse_dates=['buy_date', 'sell_date'])
                df_tup = (bull_df, bear_df)
                df, show_tree_lt, datetime_tdy_done = df_tup[df_idx], [
                ], pd.to_datetime(last_tdy_done, format='%Y%m%d')
                Rec_df = pd.read_csv('D:/stocks/Rec.csv')
                df_name = bull_name if df_idx == 0 else bear_name
                Rec_idx = Rec_df[Rec_df['name'] == df_name].index.to_list()[0]
                Priority = Rec_df.loc[Rec_idx, 'priority']
                if in_or_out == 'in':
                    row_cnt, start, start_p = - \
                        1, 'buy_date' if df_idx == 0 else 'sell_date', 'buy_p' if df_idx == 0 else 'sell_p'
                    for idx in range(len(df)):
                        start_date, close = df.loc[idx, start], round(
                            df.loc[idx, start_p], 2)
                        if start_date == datetime_tdy_done:
                            row_cnt += 1
                            code, select_val = df.loc[idx, 'code'], round(
                                df.loc[idx, Priority], 2) if Priority in not_percent else round(100 * df.loc[idx, Priority], 2)
                            try:
                                price_df = pd.read_csv(
                                    'D:/2016_2019/p/p' + str(code) + '.csv', parse_dates=['date'])
                            except:
                                price_df = pd.read_csv(
                                    'D:/2016_2019/p/p1000.csv', parse_dates=['date'])
                            closechg, vol = round((price_df.loc[len(price_df) - 1, 'close'] / price_df.loc[len(
                                price_df) - 2, 'close'] - 1) * 100, 2), round(price_df.loc[len(price_df) - 1, 'vol'], 2)
                            show_tree_lt.append((code, name_lt[code_lt.index(str(code))], start_date.strftime(
                                '%Y-%m-%d'), vol, close, closechg, select_val))
                    if show_tree_lt != []:
                        show_tree_lt.sort(
                            key=lambda z: z[6], reverse=True if Rec_df.loc[Rec_idx, 'seq'] == 'descend' else False)
                        ResTable = tk.Toplevel()
                        ResTable.title(Title)
                        ResTable.geometry('820x450+0+0')
                        ResTable.iconbitmap('D:/stocks/stock.ico')
                        vbar = tk.Scrollbar(
                            ResTable, orient='vertical', takefocus=1, cursor='hand2', relief='flat')
                        col_tags = (
                            "Column 2", "Column 3", "Column 4", "Column 5", "Column 6", "Column 7", "Column 8")
                        col_wid_lt = (50, 95, 95, 85, 85, 70, 145)
                        tree = ttk.Treeview(ResTable, height=20, show='headings', column=col_tags,
                                            yscrollcommand=vbar.set)
                        vbar.config(command=tree.yview)
                        vbar.pack(side=tk.RIGHT, fill='y', padx=5,
                                  pady=5, ipadx=2, ipady=2)
                        for ctag in col_tags:
                            col_wid = col_wid_lt[col_tags.index(ctag)]
                            tree.column(ctag, width=col_wid, minwidth=col_wid,
                                        anchor=tk.E if ctag != "Column 3" else tk.CENTER)
                        columns = ('代號', '名稱', '進場日期', '成交量', '收盤價', '漲跌幅%',
                                   reverse_select[Priority] if Priority in not_percent else reverse_select[Priority] + '%')
                        for col in columns:
                            col_index = col_tags[columns.index(col)]
                            tree.heading(col_index, text=col, anchor=tk.CENTER,
                                         command=lambda _col=col_index: treeview_sort_column(tree, _col, False))
                        for row_idx, row in enumerate(show_tree_lt):
                            if float(row[5]) > 0:
                                color_chg = 'red'
                            elif float(row[5]) < 0:
                                color_chg = 'green'
                            else:
                                color_chg = 'black'
                            tree.insert('', row_idx,
                                        values=row, tag=color_chg)
                        tree.tag_configure(
                            'red', foreground='#ff0089', font=tkfont.nametofont('TkTextFont'))
                        tree.tag_configure(
                            'green', foreground='#008B8B', font=tkfont.nametofont('TkTextFont'))
                        tree.tag_configure(
                            'black', font=tkfont.nametofont('TkTextFont'))
                        tree.pack(fill='both', padx=5,
                                  pady=5, ipadx=2, ipady=2)
                        tree.bind(
                            '<Double-Button-1>', lambda x: selectItem(tree.item(tree.focus()), tree.focus()))
                    else:
                        note = '無多單進場訊號' if df_idx == 0 else '無空單進場訊號'
                        messagebox.showinfo('篩選結果', note)
                elif in_or_out == 'out':
                    if df_idx == 1:
                        start, start_p, in_p = 'buy_date', 'buy_p', 'sell_p'
                    else:
                        start, start_p, in_p = 'sell_date', 'sell_p', 'buy_p'
                    row_cnt = -1
                    for idx in range(len(df)):
                        start_date, close = df.loc[idx, start], round(
                            df.loc[idx, start_p], 2)
                        if start_date == datetime_tdy_done:
                            row_cnt += 1
                            code, select_val, in_price, return_val = df.loc[idx, 'code'], round(df.loc[idx, Priority], 2) if Priority in not_percent else round(100 * df.loc[idx, Priority], 2), round(df.loc[idx, in_p], 2), round(
                                ((df.loc[idx, 'sell_p'] * (1 - fee - tax)) / (df.loc[idx, 'buy_p'] * (fee + 1)) - 1) * 100, 2) if df_idx == 0 else round(100 * ((df.loc[idx, 'sell_p'] * (1 - margin * (fee + tax))) / (df.loc[idx, 'buy_p'] * (fee + 1)) - 1), 2)
                            try:
                                price_df = pd.read_csv(
                                    'D:/2016_2019/p/p' + str(code) + '.csv', parse_dates=['date'])
                            except:
                                price_df = pd.read_csv(
                                    'D:/2016_2019/p/p1000.csv', parse_dates=['date'])
                            closechg, vol = round((price_df.loc[len(price_df) - 1, 'close'] / price_df.loc[len(
                                price_df) - 2, 'close'] - 1) * 100, 2), round(price_df.loc[len(price_df) - 1, 'vol'], 2)
                            show_tree_lt.append((code, name_lt[code_lt.index(str(code))], df.loc[idx, 'sell_date' if df_idx == 1 else 'buy_date'].strftime(
                                '%Y-%m-%d'), start_date.strftime('%Y-%m-%d'), vol, in_price, close, return_val, closechg, select_val))
                    if show_tree_lt != []:
                        show_tree_lt.sort(
                            key=lambda z: z[9], reverse=True if Rec_df.loc[Rec_idx, 'seq'] == 'descend' else False)
                        ResTable = tk.Toplevel()
                        ResTable.title(Title)
                        ResTable.geometry('980x450+0+0')
                        ResTable.iconbitmap('D:/stocks/stock.ico')
                        vbar = tk.Scrollbar(
                            ResTable, orient='vertical', takefocus=1, cursor='hand2', relief='flat')
                        col_tags = ("Column 2", "Column 3", "Column 4", "Column 5", "Column 6",
                                                "Column 7", "Column 8", "Column 9", "Column 10", "Column 11")
                        col_wid_lt = (50, 95, 95, 95, 85, 80, 80, 70, 70, 145)
                        tree = ttk.Treeview(ResTable, height=20, show='headings', column=col_tags,
                                            yscrollcommand=vbar.set)
                        vbar.config(command=tree.yview)
                        vbar.pack(side=tk.RIGHT, fill='y', padx=5,
                                  pady=5, ipadx=2, ipady=2)
                        for ctag in col_tags:
                            col_wid = col_wid_lt[col_tags.index(ctag)]
                            tree.column(ctag, width=col_wid, minwidth=col_wid,
                                        anchor=tk.E if ctag != "Column 3" else tk.CENTER)
                        columns = ('代號', '名稱', '進場日期', '出場日期', '成交量', '進場價', '收盤價', '報酬率%', '漲跌幅%',
                                   reverse_select[Priority] if Priority in not_percent else reverse_select[Priority] + '%')
                        for col in columns:
                            col_index = col_tags[columns.index(col)]
                            tree.heading(col_index, text=col, anchor=tk.CENTER,
                                         command=lambda _col=col_index: treeview_sort_column(tree, _col, False))
                        for row_idx, row in enumerate(show_tree_lt):
                            if float(row[7]) > 0:
                                color_chg = 'red'
                            elif float(row[7]) < 0:
                                color_chg = 'green'
                            else:
                                color_chg = 'black'
                            tree.insert('', row_idx,
                                        values=row, tag=color_chg, )
                        tree.tag_configure(
                            'red', foreground='#ff0089', font=tkfont.nametofont('TkTextFont'))
                        tree.tag_configure(
                            'green', foreground='#008B8B', font=tkfont.nametofont('TkTextFont'))
                        tree.tag_configure(
                            'black', font=tkfont.nametofont('TkTextFont'))
                        tree.pack(fill='both', padx=5,
                                  pady=5, ipadx=2, ipady=2)
                        tree.bind(
                            '<Double-Button-1>', lambda x: selectItem(tree.item(tree.focus()), tree.focus()))
                    else:
                        note = '無多單出場訊號' if df_idx == 0 else '無空單出場訊號'
                        messagebox.showinfo('篩選結果', note)
                else:
                    if df_idx == 1:
                        start, out_p, in_p = 'buy_date', 'buy_p', 'sell_p'
                    else:
                        start, out_p, in_p = 'sell_date', 'sell_p', 'buy_p'
                    row_cnt = -1
                    for idx in range(len(df)):
                        start_date, out_price = df.loc[idx,
                                                       start], df.loc[idx, out_p]
                        row_cnt += 1
                        code, select_val, in_price = df.loc[idx, 'code'], round(
                            df.loc[idx, Priority], 2) if Priority in not_percent else round(100 * df.loc[idx, Priority], 2), df.loc[idx, in_p]
                        try:
                            price_df = pd.read_csv(
                                'D:/2016_2019/p/p' + str(code) + '.csv', parse_dates=['date'])
                        except:
                            price_df = pd.read_csv(
                                'D:/2016_2019/p/p1000.csv', parse_dates=['date'])
                        now_price = price_df.loc[len(price_df) - 1, 'close']
                        closechg, vol = round((now_price / price_df.loc[
                            len(price_df) - 2, 'close'] - 1) * 100, 2), round(price_df.loc[len(price_df) - 1, 'vol'], 2)
                        if start_date.strftime('%Y-%m-%d') == '2000-01-01' and df_idx == 0:
                            return_val = round(
                                ((now_price * (1 - fee - tax)) / (in_price * (fee + 1)) - 1) * 100, 2)
                        elif start_date.strftime('%Y-%m-%d') == '2000-01-01' and df_idx == 1:
                            return_val = round(
                                100 * ((in_price * (1 - margin * (fee + tax))) / (now_price * (fee + 1)) - 1), 2)
                        elif start_date.strftime('%Y-%m-%d') != '2000-01-01' and df_idx == 0:
                            return_val = round(
                                ((out_price * (1 - fee - tax)) / (in_price * (fee + 1)) - 1) * 100, 2)
                        else:
                            return_val = round(
                                100 * ((in_price * (1 - margin * (fee + tax))) / (out_price * (fee + 1)) - 1), 2)
                        real_out_date = start_date.strftime(
                            '%Y-%m-%d') if start_date.strftime('%Y-%m-%d') != '2000-01-01' else '未出場'
                        show_tree_lt.append((code, name_lt[code_lt.index(str(code))], df.loc[idx, 'sell_date' if df_idx == 1 else 'buy_date'].strftime(
                            '%Y-%m-%d'), real_out_date, vol, round(in_price, 2), round(now_price, 2), return_val, closechg, select_val))
                    if show_tree_lt != []:
                        show_tree_lt.sort(key=lambda z: z[7], reverse=True)
                        ResTable = tk.Toplevel()
                        ResTable.title(Title)
                        ResTable.geometry('980x450+0+0')
                        ResTable.iconbitmap('D:/stocks/stock.ico')
                        vbar = tk.Scrollbar(
                            ResTable, orient='vertical', takefocus=1, cursor='hand2', relief='flat')
                        col_tags = ("Column 2", "Column 3", "Column 4", "Column 5", "Column 6",
                                                "Column 7", "Column 8", "Column 9", "Column 10", "Column 11")
                        col_wid_lt = (50, 95, 95, 95, 85, 80, 80, 70, 70, 145)
                        tree = ttk.Treeview(ResTable, height=20, show='headings', column=col_tags,
                                            yscrollcommand=vbar.set)
                        vbar.config(command=tree.yview)
                        vbar.pack(side=tk.RIGHT, fill='y', padx=5,
                                  pady=5, ipadx=2, ipady=2)
                        for ctag in col_tags:
                            col_wid = col_wid_lt[col_tags.index(ctag)]
                            tree.column(ctag, width=col_wid, minwidth=col_wid,
                                        anchor=tk.E if ctag != "Column 3" else tk.CENTER)
                        columns = ('代號', '名稱', '進場日期', '出場日期', '成交量', '進場價', '收盤價', '報酬率%', '漲跌幅%',
                                   reverse_select[Priority] if Priority in not_percent else reverse_select[Priority] + '%')
                        for col in columns:
                            col_index = col_tags[columns.index(col)]
                            tree.heading(col_index, text=col, anchor=tk.CENTER,
                                         command=lambda _col=col_index: treeview_sort_column(tree, _col, False))
                        for row_idx, row in enumerate(show_tree_lt):
                            if float(row[7]) > 0:
                                color_chg = 'red'
                            elif float(row[7]) < 0:
                                color_chg = 'green'
                            else:
                                color_chg = 'black'
                            tree.insert('', row_idx,
                                        values=row, tag=color_chg)
                        tree.tag_configure(
                            'red', foreground='#ff0089', font=tkfont.nametofont('TkTextFont'))
                        tree.tag_configure(
                            'green', foreground='#008B8B', font=tkfont.nametofont('TkTextFont'))
                        tree.tag_configure(
                            'black', font=tkfont.nametofont('TkTextFont'))
                        tree.pack(fill='both', padx=5,
                                  pady=5, ipadx=2, ipady=2)
                        tree.bind(
                            '<Double-Button-1>', lambda x: selectItem(tree.item(tree.focus()), tree.focus()))
        else:
            if len(bull_name) == 0 and len(bear_name) != 0:
                messagebox.showwarning(
                    '設定', '至少設定一個多單策略，方法如下:\n1. 請回到主選單，點選右下角的按鈕\n2. 點選「檢視策略」，選擇一個策略\n3. 點選「多單進出點位」\n4.點選「設為策略」，即可新增一個多單策略')
            elif len(bull_name) != 0 and len(bear_name) == 0:
                messagebox.showwarning(
                    '設定', '至少設定一個空單策略，方法如下:\n1. 請回到主選單，點選右下角的按鈕\n2. 點選「檢視策略」，選擇一個策略\n3. 點選「空單進出點位」\n4.點選「設為策略」，即可新增一個空單策略')
            else:
                messagebox.showwarning(
                    '設定', '至少設定一個多單及空單策略，方法如下:\n1. 請回到主選單，點選右下角的按鈕\n2. 點選「檢視策略」，選擇一個策略\n3. 點選「多單進出點位」或「空單進出點位」\n4.點選「設為策略」，即可新增一個策略')
    root.destroy()

    def click_enter(self):
        send_strategy(bull_lt[comBull.get()], bear_lt[comBear.get()], ViewWin)
    ViewWin = tk.Toplevel()
    ViewWin.geometry('345x155+307+200')
    ViewWin.iconbitmap('D:/stocks/stock.ico')
    ViewWin.title('篩選股票')
    with open('D:/stocks/StrategyList.txt', newline='\n', encoding='utf-8') as slist:
        all_files = list(csv.reader(slist))
    bull_lt, bear_lt = {}, {}
    for f in all_files:
        if f[0][0] == 'b':
            bull_lt[f[1]] = f[0]
        else:
            bear_lt[f[1]] = f[0]
    BullLabel = tk.Label(ViewWin, text='選擇多單策略')
    BullLabel.grid(row=0, column=0, padx=8, pady=8, ipadx=2, ipady=2)
    comBull = ttk.Combobox(
        ViewWin, width=19, values=tuple(bull_lt.keys()), state='readonly')
    comBull.grid(row=0, column=1, padx=8, pady=8, ipadx=2, ipady=2)
    if bull_lt != []:
        comBull.current(0)
    BearLabel = tk.Label(ViewWin, text='選擇空單策略')
    BearLabel.grid(row=1, column=0, padx=8, pady=8, ipadx=2, ipady=2)
    comBear = ttk.Combobox(
        ViewWin, width=19, values=tuple(bear_lt.keys()), state='readonly')
    comBear.grid(row=1, column=1, padx=8, pady=8, ipadx=2, ipady=2)
    if bear_lt != []:
        comBear.current(0)
    draw_btn = ttk.Button(ViewWin, text='篩選',
                          command=lambda: send_strategy(bull_lt[comBull.get()], bear_lt[comBear.get()], ViewWin))
    draw_btn.grid(row=3, column=0, columnspan=2,
                  padx=8, pady=8, ipadx=2, ipady=2)
    ViewWin.bind("<Return>", click_enter)


def View(root):
    def send_parameter(rec_df, bull, bear):
        folder, bull_idx, bear_idx = 'D:/2016_2019/backtest/', rec_df[rec_df['name'] == bull].index.to_list()[
            0], rec_df[rec_df['name'] == bear].index.to_list()[0]
        ShowResult(folder + bull, folder + bear, True, True,
                   {'多單本金': rec_df.loc[bull_idx, 'principle'],
                    '空單本金': rec_df.loc[bear_idx, 'principle']},
                   {'多單篩選依據': reverse_select[rec_df.loc[bull_idx, 'priority']], '空單篩選依據': reverse_select[rec_df.loc[bull_idx, 'priority']],
                    '多單排序': '由高到低' if rec_df.loc[bull_idx, 'seq'] == 'descend' else '由低到高', '空單排序': '由高到低' if rec_df.loc[bear_idx, 'seq'] == 'descend' else '由低到高'},
                   {'多單最低現金': rec_df.loc[bull_idx, 'mincash'], '空單最低現金': rec_df.loc[bear_idx, 'mincash'],
                    '多單金額上限': rec_df.loc[bull_idx, 'uplimit'], '空單金額上限': rec_df.loc[bear_idx, 'uplimit'],
                    '多單投入金額': rec_df.loc[bull_idx, 'invest'], '空單投入金額': rec_df.loc[bear_idx, 'invest']}, ViewWin)
    rec_df = pd.read_csv('D:/stocks/Rec.csv')
    all_files = [rec_df.loc[row, 'name'] for row in range(len(rec_df))]
    bull_lt, bear_lt = [], []
    for f in all_files:
        if f[0] == 'b':
            bull_lt.append(f)
        else:
            bear_lt.append(f)
    root.destroy()
    ViewWin = tk.Toplevel()
    ViewWin.geometry('348x150+307+200')
    ViewWin.iconbitmap('D:/stocks/stock.ico')
    ViewWin.title('繪製圖表')
    BullLabel = tk.Label(ViewWin, text='選擇多單策略')
    BullLabel.grid(row=0, column=0, padx=8, pady=8, ipadx=2, ipady=2)
    comBull = ttk.Combobox(ViewWin, width=19, values=bull_lt, state='readonly')
    comBull.grid(row=0, column=1, padx=8, pady=8, ipadx=2, ipady=2)
    comBull.current(0)
    BearLabel = tk.Label(ViewWin, text='選擇空單策略')
    BearLabel.grid(row=1, column=0, padx=8, pady=8, ipadx=2, ipady=2)
    comBear = ttk.Combobox(ViewWin, width=19, values=bear_lt, state='readonly')
    comBear.grid(row=1, column=1, padx=8, pady=8, ipadx=2, ipady=2)
    comBear.current(0)
    draw_btn = ttk.Button(ViewWin, text='繪製績效圖表',
                          command=lambda: send_parameter(rec_df, comBull.get(), comBear.get()))
    draw_btn.grid(row=3, column=0, columnspan=2,
                  padx=8, pady=8, ipadx=2, ipady=2)


def Compare(root):
    def BtnPressed(comVal_lt):
        plot_dict, type_lt, non_overlap, strat_dict = {}, [
            '多單策略', '空單策略', '組合策略'], [], {}
        for e, group in enumerate(comVal_lt):
            seq = 0
            for val in group:
                if val != 'N/A' and val not in non_overlap:
                    non_overlap.append(val)
                    seq += 1
                    plot_dict[type_lt[e] + str(seq)] = pd.read_csv(
                        'D:/2016_2019/cp/' + val, parse_dates=['date'])
                    strat_dict[type_lt[e] + str(seq)] = val
        if len(plot_dict) >= 2:
            cp_plot(plot_dict)
        else:
            backtest_msg('view')
    all_files = listdir(r"D:\2016_2019\cp")
    bull_lt, bear_lt, combo_lt = [], [], []
    for f in all_files:
        if f[:3] == 'cpb':
            bull_lt.append(f)
        elif f[:3] == 'cps':
            bear_lt.append(f)
        elif f[:5] == 'total' and f[-3:] == 'csv':
            combo_lt.append(f)
    files_tup = (bull_lt, bear_lt, combo_lt)
    for f_lt in files_tup:
        f_lt.sort(key=lambda x: int(x.split('-')[1][:-4]))
        f_lt.insert(0, 'N/A')
    root.destroy()
    ViewWin = tk.Toplevel()
    ViewWin.geometry('958x258+0+290')
    ViewWin.iconbitmap('D:/stocks/stock.ico')
    ViewWin.title('綜合比較')
    BullLabelF = tk.LabelFrame(ViewWin, text='選擇多單策略', padx=6, pady=6)
    BullLabelF.grid(row=0, column=0, padx=6, pady=6)
    comBull01 = ttk.Combobox(BullLabelF, width=28,
                             values=bull_lt, state='readonly')
    comBull01.grid(row=0, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comBull01.current(0)
    comBull02 = ttk.Combobox(BullLabelF, width=28,
                             values=bull_lt, state='readonly')
    comBull02.grid(row=1, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comBull02.current(0)
    comBull03 = ttk.Combobox(BullLabelF, width=28,
                             values=bull_lt, state='readonly')
    comBull03.grid(row=2, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comBull03.current(0)
    comBull04 = ttk.Combobox(BullLabelF, width=28,
                             values=bull_lt, state='readonly')
    comBull04.grid(row=3, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comBull04.current(0)
    BearLabelF = tk.LabelFrame(ViewWin, text='選擇空單策略', padx=6, pady=6)
    BearLabelF.grid(row=0, column=1, padx=6, pady=6)
    comBear01 = ttk.Combobox(BearLabelF, width=28,
                             values=bear_lt, state='readonly')
    comBear01.grid(row=0, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comBear01.current(0)
    comBear02 = ttk.Combobox(BearLabelF, width=28,
                             values=bear_lt, state='readonly')
    comBear02.grid(row=1, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comBear02.current(0)
    comBear03 = ttk.Combobox(BearLabelF, width=28,
                             values=bear_lt, state='readonly')
    comBear03.grid(row=2, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comBear03.current(0)
    comBear04 = ttk.Combobox(BearLabelF, width=28,
                             values=bear_lt, state='readonly')
    comBear04.grid(row=3, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comBear04.current(0)
    ComboLabelF = tk.LabelFrame(ViewWin, text='選擇組合策略', padx=6, pady=6)
    ComboLabelF.grid(row=0, column=2, padx=6, pady=6)
    comCombo01 = ttk.Combobox(ComboLabelF, width=28,
                              values=combo_lt, state='readonly')
    comCombo01.grid(row=0, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comCombo01.current(0)
    comCombo02 = ttk.Combobox(ComboLabelF, width=28,
                              values=combo_lt, state='readonly')
    comCombo02.grid(row=1, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comCombo02.current(0)
    comCombo03 = ttk.Combobox(ComboLabelF, width=28,
                              values=combo_lt, state='readonly')
    comCombo03.grid(row=2, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comCombo03.current(0)
    comCombo04 = ttk.Combobox(ComboLabelF, width=28,
                              values=combo_lt, state='readonly')
    comCombo04.grid(row=3, column=0, padx=6, pady=6, ipadx=2, ipady=2)
    comCombo04.current(0)
    view_btn = ttk.Button(ViewWin, text='查看圖表', command=lambda: BtnPressed([[comBull01.get(), comBull02.get(), comBull03.get(), comBull04.get()],
                                                                            [comBear01.get(), comBear02.get(), comBear03.get(), comBear04.get()], [comCombo01.get(), comCombo02.get(), comCombo03.get(), comCombo04.get()]]))
    view_btn.grid(row=1, column=0, columnspan=3, pady=3, ipadx=2, ipady=2)


def ShowTable(root, fname):
    root.destroy()
    all_files = listdir('D:/2016_2019/cp')
    full_path_lt = []
    for f in all_files:
        full_path_lt.append('D:/2016_2019/cp/' + f)
    if fname == None or fname not in full_path_lt:
        backtest_msg('ShowTable')
    else:
        with open(fname) as jsonfile:
            table_lt = json.load(jsonfile)
        ResTable = tk.Toplevel()
        ResTable.title(fname)
        ResTable.geometry('815x505+253+0')
        ResTable.iconbitmap('D:/stocks/stock.ico')
        TableFm = tk.Frame(ResTable)
        TableFm.pack(side=tk.TOP, fill='x', padx=6, pady=6)
        vbar = tk.Scrollbar(TableFm, orient='vertical',
                            takefocus=1, cursor='hand2', relief='flat')
        tree = ttk.Treeview(TableFm, height=20, column=("Column 2", "Column 3", "Column 4"),
                            yscrollcommand=vbar.set)
        vbar.config(command=tree.yview)
        vbar.pack(side=tk.RIGHT, fill='y', padx=5, pady=5, ipadx=2, ipady=2)
        tree.column("#0", width=200, minwidth=120)
        tree.column("Column 2", width=180, minwidth=160)
        tree.column("Column 3", width=200, minwidth=160)
        tree.column("Column 4", width=200, minwidth=160)
        tree.heading("#0", text='項目', anchor=tk.W)
        bull_fname = fname[:13] + 'backtest/' + \
            fname[21:26] + fname[31:43] + 'csv'
        bear_fname = fname[:13] + 'backtest/' + fname[26:43] + 'csv'
        tree.heading("Column 2", text='多單', anchor=tk.W)
        tree.heading("Column 3", text='空單', anchor=tk.W)
        tree.heading("Column 4", text='合併', anchor=tk.W)
        for e, heading in enumerate(heading_lt):
            if e <= 2:
                total_val = []
                for seq in range(3):
                    total_cnt = 0
                    for v1 in list(table_lt[e].values())[:11]:
                        total_cnt += sum(mon_cnt[seq]
                                         for mon_cnt in v1.values())
                    total_val.append(total_cnt)
                top_row = tree.insert("", e, text=heading,
                                      values=total_val, tag=('black',))
                row_idx = 0
                for cnt_key, cnt_val in list(table_lt[e].items())[:11]:
                    sec_row = tree.insert(top_row, row_idx, text=cnt_key + '年',
                                          values=(sum(mon_cnt[0] for mon_cnt in cnt_val.values()),
                                                  sum(mon_cnt[1]
                                                      for mon_cnt in cnt_val.values()),
                                                  sum(mon_cnt[2] for mon_cnt in cnt_val.values())),
                                          tags=('odd2',) if int(cnt_key) % 2 == 1 else ('even2',))
                    row_idx += 1
                    end_idx = 0
                    for k2, v2 in cnt_val.items():
                        tree.insert(sec_row, 'end', text=k2 + '月', values=v2,
                                    tags=('odd3',) if int(k2) % 2 == 1 else ('even3',))
                        end_idx += 1
            elif e <= 16 or e >= 20:
                if table_lt[0][heading] > 0 and table_lt[1][heading] > 0 and table_lt[2][heading] > 0:
                    tag = ('red',)
                elif table_lt[0][heading] < 0 and table_lt[1][heading] < 0 and table_lt[2][heading] < 0:
                    tag = ('green',)
                else:
                    tag = ('black',)
                tree.insert("", 'end', text=heading,
                            values=(
                                table_lt[0][heading], table_lt[1][heading], table_lt[2][heading]),
                            tags=tag)
        tree.tag_configure('odd2', font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('even2', background='#EEEEEE',
                           font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('odd3', font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('even3', background='#DDDDDD',
                           font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('red', foreground='#ff0089',
                           font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('green', foreground='#008B8B',
                           font=tkfont.nametofont('TkTextFont'))
        tree.tag_configure('black', font=tkfont.nametofont('TkTextFont'))
        tree.pack(fill='both', padx=5, pady=5, ipadx=2, ipady=2)
        BtnFm = tk.Frame(ResTable)
        BtnFm.pack(side=tk.TOP)
        bull_btn = ttk.Button(BtnFm, text='多單進出場點位',
                              command=lambda: Annotate(ResTable, bull_fname))
        bull_btn.pack(side=tk.LEFT, padx=80, pady=6, ipadx=4, ipady=4)
        bear_btn = ttk.Button(BtnFm, text='空單進出場點位',
                              command=lambda: Annotate(ResTable, bear_fname))
        bear_btn.pack(side=tk.RIGHT, padx=80, pady=6, ipadx=4, ipady=4)


def ViewTable(root):
    def click_enter(self):
        ShowTable(ViewWin, 'D:/2016_2019/cp/' + comFile.get())
    root.destroy()
    ViewWin = tk.Toplevel()
    ViewWin.geometry('350x180+307+200')
    ViewWin.iconbitmap('D:/stocks/stock.ico')
    ViewWin.title('檢視策略')
    ViewFrame = tk.LabelFrame(ViewWin, text='選擇檔案', padx=8, pady=8)
    ViewFrame.pack(fill='both', padx=8, pady=8, ipadx=4, ipady=4)
    jsonfile_lt = [f for f in listdir(
        'D:/2016_2019/cp') if f[-4:] == 'json' and int(f[-15:-5]) >= 2012082304]
    jsonfile_lt.sort(key=lambda t: int(t[-15:-5]))
    comFile = ttk.Combobox(ViewFrame, width=33,
                           values=jsonfile_lt, state='readonly')
    comFile.pack(fill='x', padx=8, pady=8, ipadx=2, ipady=2)
    show_btn = ttk.Button(ViewFrame, text='顯示表格', command=lambda: ShowTable(
        ViewWin, 'D:/2016_2019/cp/' + comFile.get()))
    show_btn.pack(fill='x', padx=8, pady=8, ipadx=2, ipady=2)
    ViewWin.bind("<Return>", click_enter)


def ViewPage(root):
    root.wm_state('iconic')
    SViewWin = tk.Toplevel()
    SViewWin.geometry('250x186+307+200')
    SViewWin.title('績效檢視')
    SViewWin.iconbitmap('D:/stocks/stock.ico')
    compare_btn = ttk.Button(SViewWin, text='綜合比較',
                             command=lambda: Compare(SViewWin))
    compare_btn.pack(fill='both', padx=8, pady=8)
    build_btn = ttk.Button(SViewWin, text='繪製圖表',
                           command=lambda: View(SViewWin))
    build_btn.pack(fill='both', padx=8, pady=8)
    view_btn = ttk.Button(SViewWin, text='檢視策略',
                          command=lambda: ViewTable(SViewWin))
    view_btn.pack(fill='both', padx=8, pady=8)
    ret_btn = ttk.Button(SViewWin, text='篩選股票',
                         command=lambda: Choose(SViewWin))
    ret_btn.pack(fill='both', padx=8, pady=8)


def Update():
    time_now = datetime.now()
    last_day = time_now - timedelta(days=1)
    last_day02 = time_now - timedelta(days=2)
    weekday = time_now.isoweekday()
    with open('D:/stocks/tdy_done.txt', newline='\n', encoding='utf-8') as tdone:
        last_done = list(csv.reader(tdone))[-1][0]
    if last_done == time_now.strftime('%Y%m%d') or (weekday == 6 and last_day.strftime('%Y%m%d') == last_done) or (weekday == 7 and last_day02.strftime('%Y%m%d') == last_done) or (time_now - pd.to_datetime(last_done, format='%Y%m%d')).seconds / 3600 < 21.5:
        backtest_msg('update ok')
    else:
        backtest_msg('start update')
        import requests

        def Daily_Update(n):
            hd = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}
            start_url = 'https://www.twse.com.tw/indicesReport/MI_5MINS_HIST?response=json&date='
            with open('D:/stocks/tdy_done.txt', newline='\n', encoding='utf-8') as tdonef:
                tdy_done_lt = [donerow[0] for donerow in list(
                    csv.reader(tdonef)) if len(donerow) != 0]
                last_day = tdy_done_lt[-1]
            now_date = datetime.today()
            begin_date, date_list, msg_lt, not_done_dict = pd.to_datetime(
                last_day, format='%Y%m%d'), [], [], {}
            print(begin_date, now_date, '相差:',
                  round((now_date - begin_date).seconds / 3600, 2), '小時')
            while begin_date < now_date:
                begin_date += timedelta(days=1)
                new_date = begin_date.strftime('%Y%m') + '01'
                if new_date not in date_list:
                    date_list.append(new_date)
            print('date:', date_list)
            for d in date_list:
                try:
                    print(start_url + d)
                    res = requests.get(start_url + d, headers=hd, timeout=140)
                    data = json.loads(res.text)
                except:
                    traceback.print_exc()
                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                        erf.write(traceback.format_exc())
                    if n <= 10:
                        n += 1
                        time.sleep(60 + n)
                        return Daily_Update(n)
                    else:
                        return 1
                else:
                    if data['stat'] == 'OK':
                        text_lt = data['data']
                        for line in text_lt:
                            split_date = line[0].split('/')
                            trade_date = str(
                                int(split_date[0]) + 1911) + split_date[1] + split_date[2]
                            if trade_date not in tdy_done_lt:
                                print(trade_date)
                                with open('D:/stocks/tdy.txt', 'a', newline='\n', encoding='utf-8') as tf:
                                    wr = csv.writer(tf)
                                    wr.writerow([trade_date])
                                error_dict = {}
                                try:
                                    tdy_fut = trade_date[:4] + '/' + \
                                        trade_date[4:6] + '/' + trade_date[6:]
                                    site_and_name = [['https://www.taifex.com.tw/cht/3/totalTableDateDown', 'total'],
                                                     ['https://www.taifex.com.tw/cht/3/futAndOptDateDown', 'FutOpt'],
                                                     ['https://www.taifex.com.tw/cht/3/futContractsDateDown', 'Fut'],
                                                     ['https://www.taifex.com.tw/cht/3/optContractsDateDown', 'Opt'],
                                                     ['https://www.taifex.com.tw/cht/3/callsAndPutsDateDown', 'CallPut'],
                                                     ['https://www.taifex.com.tw/cht/3/largeTraderFutDown', 'BigFut'],
                                                     ['https://www.taifex.com.tw/cht/3/largeTraderOptDown', 'BigOpt'],
                                                     ['https://www.taifex.com.tw/cht/3/dlPcRatioDown', 'PCratio']]
                                    for ele in site_and_name:
                                        fn = ele[1] + trade_date + '.csv'
                                        if fn not in listdir(fut_path):
                                            st = time.time()
                                            getFut(ele[0], fn, tdy_fut, 0)
                                            end = time.time()
                                            if end - st < 1:
                                                time.sleep(
                                                    random.uniform(1, 1.3))
                                            else:
                                                time.sleep(1)
                                        else:
                                            print(fn, 'has_updated')
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    getCapRed(0)
                                    getOtcDecap(0)
                                    getDiv(0)
                                    time.sleep(1.5)
                                    getOtcDiv(0)
                                    getStopMar(0)
                                    getOtcMar(0)
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    with open('D:/stocks/ret_done.txt', newline='\n', encoding='utf-8') as prd:
                                        done_lt = [row[0]
                                                   for row in csv.reader(prd)]
                                    if trade_date not in done_lt:
                                        getRetIndex(trade_date, 0)
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    print('Check for taiex close:', trade_date)
                                    with open('D:/stocks/taiex_close_done.txt', newline='\n', encoding='utf-8') as prd:
                                        date_rd = [r[0]
                                                   for r in csv.reader(prd)]
                                        if trade_date not in date_rd:
                                            getIndex(trade_date, 0)
                                        else:
                                            print(
                                                'Data for ' + trade_date + ' has already done')
                                    time.sleep(2)
                                    print('Check for taiex OHLC:', trade_date)
                                    with open('D:/stocks/taiex_OHLC_done.txt', newline='\n', encoding='utf-8') as prd:
                                        date_rd = [r[0]
                                                   for r in csv.reader(prd)]
                                        if trade_date not in date_rd:
                                            getOHLC(trade_date, 0)
                                        else:
                                            print(
                                                'Data for ' + trade_date + ' has already done')
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    import new_stk
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    import otc_pr01
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    import twse_pr01
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    import otc_inv03
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                    time.sleep(15)
                                    print('Try to download again: OTC INV')
                                    import otc_inv03
                                try:
                                    import daily_inv
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                    time.sleep(15)
                                    print('Try to download again: TWSE INV')
                                    import daily_inv
                                try:
                                    import getDivCap
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    import otc_lend
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                    time.sleep(15)
                                    print('Try to download again: OTC LEND')
                                    import otc_lend
                                try:
                                    import twse_lend
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                    time.sleep(15)
                                    print('Try to download again: TWSE LEND')
                                    import twse_lend
                                try:
                                    import otc_fm
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                    time.sleep(15)
                                    print('Try to download again: OTC FM')
                                    import otc_fm
                                try:
                                    import twse_fm
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                    time.sleep(15)
                                    print('Try to download again: TWSE FM')
                                    import twse_fm
                                try:
                                    import TAIEX_Update
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                try:
                                    import TPEX_Update
                                except:
                                    traceback.print_exc()
                                    with open('D:/stocks/error.txt', 'a', newline='\n', encoding='utf-8') as erf:
                                        erf.write(traceback.format_exc())
                                mail_lt = ['output_error.txt',  'error.txt',  'no_date.txt',
                                           'No_trade.txt',
                                           'wrong_name.txt', 'No_fm.txt', 'No_Index.txt', 'No_otc_lend.txt',
                                           'No_TAIEX.txt',
                                           'No_twse_lend.txt', 'No_TPEX.txt', 'No_twse_inv.txt', 'No_otc_inv.txt']
                                done_lt = ['otc_fm_done.txt', 'otc_lend_done.txt', 'otc_pr_done.txt', 'otc01_done.txt',
                                           'twse_pr_done.txt', 'ret_done.txt', 'taiex_close_done.txt',
                                           'TAIEX_inv_done.txt',
                                           'taiex_OHLC_done.txt', 'TPEX_inv_done.txt', 'twse_fm_done.txt',
                                           'twse_inv_done.txt',
                                           'twse_lend_done.txt', 'DivCap_done.txt']
                                with open('D:/stocks/tdy.txt', newline='\n', encoding='utf-8') as tdyfile:
                                    latest = list(csv.reader(tdyfile))[-1][0]
                                for task in done_lt:
                                    with open('D:/stocks/' + task, newline='\n', encoding='utf-8') as file:
                                        last_day = list(
                                            csv.reader(file))[-1][0]
                                    if last_day != latest and latest not in not_done_dict:
                                        not_done_dict[latest] = [task[:-9]]
                                    elif last_day != latest and latest in not_done_dict:
                                        not_done_dict[latest].append(task[:-9])
                                for mail in mail_lt:
                                    with open('D:/stocks/' + mail, newline='\n', encoding='utf-8') as errfile:
                                        file_text = list(csv.reader(errfile))
                                        if file_text != []:
                                            error_dict[mail] = ''
                                            for line in file_text:
                                                for text in line:
                                                    error_dict[mail] = error_dict[mail] + text
                                                error_dict[mail] = error_dict[mail] + '\n'
                                if not_done_dict == {}:
                                    with open('D:/stocks/tdy_done.txt', 'a', newline='\n', encoding='utf-8') as tdonef:
                                        wr = csv.writer(tdonef)
                                        wr.writerow([trade_date])
                                if error_dict != {}:
                                    err_msg = '錯誤訊息（' + latest + '）：'
                                    for key, value in error_dict.items():
                                        err_msg += '\n' + key + '：' + value
                                    msg_lt.append(err_msg)
                                with open('D:/stocks/below200.txt', newline='\n', encoding='utf-8') as b200:
                                    b200_lt = list(csv.reader(b200))
                                last_b200 = b200_lt[-1][0]
                                if code_lt[-1] != last_b200:
                                    next_stk_idx = code_lt.index(last_b200) + 1
                                    for filter_idx in range(next_stk_idx, len(code_lt)):
                                        test_code = code_lt[filter_idx]
                                        test_df = pd.read_csv(
                                            'D:/2016_2019/p/p' + str(test_code) + '.csv')
                                        if len(test_df) - 1 >= min_idx:
                                            with open('D:/stocks/below200.txt', 'a', newline='\n', encoding='utf-8') as b200:
                                                b200wr = csv.writer(b200)
                                                b200wr.writerow(
                                                    [test_code, name_lt[filter_idx]])
            return [not_done_dict, msg_lt]
        rtn_msg = Daily_Update(0)
        while rtn_msg == 1:
            rtn_msg = Daily_Update(0)
        if rtn_msg[0] != {} and rtn_msg[1] != []:
            not_done_msg = '以下日期的資料未更新，可能需要重新下載：\n'
            for k, v in rtn_msg[0].items():
                not_done_msg += k + '：' + ','.join(v) + '\n'
            messagebox.showinfo('資料更新,', not_done_msg)
            messagebox.showinfo('資料更新', '\n'.join(rtn_msg[1]))
        elif rtn_msg[0] == {} and rtn_msg[1] != []:
            messagebox.showinfo('資料更新', '\n'.join(rtn_msg[1]))
            backtest_msg('update ok')
        elif rtn_msg[0] == {} and rtn_msg[1] == []:
            backtest_msg('update ok')
        else:
            not_done_msg = '以下日期的資料未更新，可能需要重新下載：\n'
            for k, v in rtn_msg[0].items():
                not_done_msg += k + '：' + ','.join(v) + '\n'
            messagebox.showinfo('資料更新,', not_done_msg)


class StkBacktest(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]
        style = ttk.Style()
        style.configure('Treeview.Heading', font=(None, 13))
        style.map('Treeview', foreground=fixed_map(
            'foreground'), background=fixed_map('background'))
        # r_style = ttk.Style().configure('red', foreground='#ff0089')
        # g_style = ttk.Style().configure('green', foreground='#008b8b')
        font = tkfont.nametofont('TkTextFont')
        font.config(size=12)
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.config(size=11)
        f1 = GradientFrame(self, relief="flat",
                           width=int(app_w), height=int(app_h))
        f1.pack(fill="both", expand=False)


class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1="#57dffa", color2="#ffc0cb", **kwargs):  # 59d6ff
        tk.Canvas.__init__(self, parent, **kwargs)
        self._color1 = color1
        self._color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        w, h, med, lateral, med_0 = 25, 25, 145, 225, 100
        self.delete('gradient')

        def Button(event):
            if w <= event.x <= med_0 and h <= event.y <= med_0:
                PlotSetting(app, 0)
            elif med <= event.x <= lateral and h <= event.y <= med_0:
                BacktestPage(app)
            elif w <= event.x <= med_0 and med <= event.y <= lateral:
                Update()
            elif med <= event.x <= lateral and med <= event.y <= lateral:
                ViewPage(app)

        def ChangeCursor(event):
            if (w <= event.x <= med_0 and h <= event.y <= med_0) or (med <= event.x <= lateral and h <= event.y <= med_0) or (w <= event.x <= med_0 and med <= event.y <= lateral) or (med <= event.x <= lateral and med <= event.y <= lateral):
                self.config(cursor='hand2')
            else:
                self.config(cursor='arrow')
        width = self.winfo_width()
        height = self.winfo_height()
        limit = height
        (r1, g1, b1) = self.winfo_rgb(self._color1)
        (r2, g2, b2) = self.winfo_rgb(self._color2)
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit
        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.search_img = ImageTk.PhotoImage(
            Image.open("D:/stocks/search3.png"), size='1x1')
        self.create_image(65, 65, anchor=tk.CENTER,
                          image=self.search_img, tags='search')
        self.backtest_img = ImageTk.PhotoImage(
            Image.open("D:/stocks/backtest3.png"), size='1x1')
        self.create_image(185, 65, anchor=tk.CENTER,
                          image=self.backtest_img, tags='backtest')
        self.update_img = ImageTk.PhotoImage(
            Image.open("D:/stocks/update3.png"), size='1x1')
        self.create_image(65, 185, anchor=tk.CENTER,
                          image=self.update_img, tags='update')
        self.view_img = ImageTk.PhotoImage(
            Image.open("D:/stocks/view3.png"), size='1x1')
        self.create_image(185, 185, anchor=tk.CENTER,
                          image=self.view_img, tags='view')
        self.bind('<Button-1>', Button)
        self.bind('<Motion>', ChangeCursor)
        self.lower("gradient")


app_w, app_h = '252', '252'
if __name__ == '__main__':
    app = tk.Tk()
    app.title('')
    app.iconbitmap('D:/stocks/stock.ico')
    app.geometry(app_w + 'x' + app_h + '+0+0')
    app.resizable(0, 0)
    app.lift()
    StkBacktest(app).pack(fill="both", expand=False)
    app.mainloop()
