#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Filename: generate_wrong_ticker_list
# @Date: 2016-12-14
# @Author: Mark Wang
# @Email: wangyouan@gmial.com

from functions import calculate_score

import os
import re
import datetime

import pandas as pd

today_str = datetime.datetime.today().strftime('%Y%m%d')
root_path = '/home/wangzg/Documents/WangYouan/research/Wrong_tickers'

temp_path = os.path.join(root_path, 'temp')
today_temp_path = os.path.join(temp_path, today_str)
data_path = os.path.join(root_path, 'data')
result_path = os.path.join(root_path, 'result_csv')

if not os.path.isdir(today_temp_path):
    os.makedirs(today_temp_path)

all_ticker_series = pd.read_excel(os.path.join(data_path, 'All Tickers_Bloomberg.xlsx'))

sdc_df = pd.read_csv(os.path.join(result_path, 'SDC_CRSP_rename_top5pc.csv'), dtype={'TargetCUSIP': str},
                     index_col=0).drop_duplicates()

all_ticker_series['len'] = all_ticker_series['BAYRY'].apply(len)
all_ticker_series = all_ticker_series[all_ticker_series.len > 2]
all_ticker_series = all_ticker_series[all_ticker_series.len < 5]

# Score constant
A4 = '4A'
A3 = '3A'
A2B2 = '2A2B'
A2B1 = '2A1B'
A2 = '2A'
A1B3 = '1A3B'
A1B2 = '1A2B'

score_dict = {40: A4,
              30: A3,
              22: A2B2,
              21: A2B1,
              20: A2,
              13: A1B3,
              12: A1B2}


def get_wrong_tickers(right_ticker):
    new_df = all_ticker_series.copy()
    new_df['score'] = new_df.BAYRY.apply(lambda x: calculate_score(right_ticker, x))
    return new_df


def get_wrong_tickers_from_row_info(row):
    ticker = row['TargetPrimaryTickerSymbol']
    name = row['TargetName']
    score_df = all_ticker_series.copy()
    score_df = score_df[score_df.BAYRY != ticker]

    if hasattr(name, 'upper'):
        tokens = re.split(r'[^a-zA-Z]+', name)
    else:
        tokens = []

    if not hasattr(ticker, '__len__'):
        ticker = ''

    # handle initials
    while '' in tokens:
        tokens.remove('')

    upper_tokens = map(lambda x: x.upper(), tokens)
    while 'INC' in upper_tokens:
        upper_tokens.remove('INC')

    while 'HOLDINGS' in upper_tokens:
        upper_tokens.remove('HOLDINGS')

    initial = ''.join(i[0] for i in upper_tokens)
    if len(initial) >= 3:
        score_df = score_df.merge(get_wrong_tickers(initial), on='BAYRY', suffixes=['', '_i'])

    if len(ticker) >= 3:
        score_df = score_df.merge(get_wrong_tickers(ticker), on='BAYRY', suffixes=['', '_t'])

    first_letters = ''.join(upper_tokens)
    if len(first_letters) >= 3:
        score_df = score_df.merge(get_wrong_tickers(first_letters[:min(4, len(first_letters))]), on='BAYRY',
                                  suffixes=['', '_f'])

    capitalized_letters = ''.join(re.findall(r'[A-Z]', name))
    if len(capitalized_letters) >= 3:
        score_df = score_df.merge(get_wrong_tickers(first_letters[:min(4, len(first_letters))]), on='BAYRY',
                                  suffixes=['', '_c'])

    def get_max_score(row):
        keys = row.keys()
        max_score = 0
        for i in keys:
            if i.startswith('score') and row[i] > max_score:
                max_score = row[i]

        return max_score

    score_df['max_score'] = score_df.apply(get_max_score, axis=1)
    score_df = score_df[score_df.max_score > 11]
    score_df['final'] = score_df.max_score.apply(lambda x: score_dict[x])
    score_df = score_df[['BAYRY', 'final']]
    groups = score_df.groupby('final')
    keys = groups.groups.keys()
    result_dict = {}
    for key in keys:
        result_dict[key] = ','.join(groups.get_group(key).BAYRY)

    return pd.Series(result_dict)


sdc_df = sdc_df.merge(sdc_df.apply(get_wrong_tickers_from_row_info, axis=1), left_index=True, right_index=True)
sdc_df.to_pickle(os.path.join(today_temp_path, 'sdc_add_wrong_tickers.p'))

# def remove_right_tickers(row):
#     wrong_tickers = row['wrong_tickers']
#     right_ticker = row['TargetPrimaryTickerSymbol']
#     if hasattr(wrong_tickers, 'split'):
#         wrong_tickers_list = wrong_tickers.split(',')
#
#         if hasattr(right_ticker, 'upper'):
#             while right_ticker in wrong_tickers_list:
#                 wrong_tickers_list.remove(right_ticker)
#
#         return ','.join(wrong_tickers_list)
#
#     else:
#         return wrong_tickers
#
# sdc_df['wrong_tickers'] = sdc_df.apply(remove_right_tickers, axis=1)

# sdc_df[['TargetName', 'TargetPrimaryTickerSymbol', 'wrong_tickers']].to_csv(
#     os.path.join(result_path, '{}_sdc_wrong_tickers.csv'.format(today_str)), index=False)

result_list = list(score_dict.values())

result_list.append('TargetName')
result_list.append('TargetPrimaryTickerSymbol')

sdc_df[result_list].to_csv(
    os.path.join(result_path, '{}_sdc_wrong_tickers.csv'.format(today_str)), index=False)