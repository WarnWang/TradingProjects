#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Project: QuestionFromProfWang
# File name: split_volume
# Author: Mark Wang
# Date: 15/8/2016

import os
from multiprocessing import Pool

import pandas as pd
import numpy as np

path = 'Stock_data'


def process_split_group_highlow(group):
    for key, df in group:
        ticker = df.ix[df.index[0], 'TICKER']
        df.to_csv(os.path.join(path, 'highlow', '{}_HL.csv'.format(ticker)), index=False)

    return 1


def process_split_group_volume(group):
    for key, df in group:
        ticker = df.ix[df.index[0], 'TICKER']
        df = df.dropna(axis=0, how='any')
        df.loc[:, 'VOL'] = df['VOL'].apply(int)
        df.to_csv(os.path.join(path, 'volume', '{}_VOL.csv'.format(ticker)), index=False)

    return 1


def process_split_group_volume_cusip(group):
    for key, df in group:
        cusip = df.ix[df.index[0], 'CUSIP']
        df = df.dropna(axis=0, how='any')
        df.loc[:, 'VOL'] = df['VOL'].apply(int)
        df.to_csv(os.path.join(path, 'volume_cusip', '{}_VOL.csv'.format(cusip)), index=False)

    return 1


def process_split_compustat_cusip(group):
    for key, df in group:
        cusip = df.ix[df.index[0], 'cusip']
        df.to_csv(os.path.join(path, 'Compustat_cusip', '{}_COMPU.csv'.format(cusip)), index=False)

    return 1


from multiprocessing import Pool

import pandas as pd
import numpy as np

df = pd.read_csv('Stock_data/price.csv', usecols=['CUSIP', 'date', 'PRC'],
                 dtype={'CUSIP': str, 'date': str})
cusip_group = df.groupby('CUSIP')
for name, group in cusip_group:
    file_name = os.path.join('Stock_data', 'price_cusip', '{}_PRC.csv'.format(name))
    group.to_csv(file_name, encoding='utf8', index=False)
del df

df = pd.read_csv('Stock_data/IBES_detail_1970_2016.csv', usecols=['CUSIP', 'FPEDATS', 'ACTUAL', 'VALUE'],
                 dtype={'CUSIP': str, 'FPEDATS': str})
cusip_group = df.groupby('CUSIP')
for name, group in cusip_group:
    file_name = os.path.join('Stock_data', 'ibes_cusip', '{}_IBES.csv'.format(name))
    group.to_csv(file_name, encoding='utf8', index=False)
del df

df = pd.read_csv('Stock_data/IBES_detail_1970_2016.csv', usecols=['OFTIC', 'FPEDATS', 'ACTUAL', 'VALUE'],
                 dtype={'FPEDATS': str})
ticker_group = df.groupby('OFTIC')
for name, group in ticker_group:
    if '/' in name:
        continue
    file_name = os.path.join('Stock_data', 'ibes', '{}_IBES.csv'.format(name))
    group.to_csv(file_name, encoding='utf8', index=False)
del df

if __name__ == "__main__":
    process_num = 6
    pool = Pool(process_num)

    # print 'Start to handle price high low'
    # price_high_low_df = pd.read_csv('Stock_data/highlow.csv', dtype={'date': str},
    #                                 usecols=['date', 'BIDLO', 'ASKHI', 'TICKER'])
    # price_high_low_group = price_high_low_df.groupby('TICKER')
    # print 'Start to split groups'
    # split_group = np.array_split(price_high_low_group, process_num)
    # print "Use {} processors to do this part".format(process_num)
    # pool.map(process_split_group_highlow, split_group)

    # print 'Start to handle volume'
    # open_close_df = pd.read_csv('Stock_data/Volume.csv', dtype={'date': str},
    #                                 usecols=['date', 'VOL', 'TICKER'])
    # volume_group = open_close_df.groupby('TICKER')
    # print 'Start to split groups'
    # split_group = np.array_split(volume_group, process_num)
    # print "Use {} processors to do this part".format(process_num)
    # pool.map(process_split_group_volume, split_group)

    # print 'Start to handle volume cusip'
    # open_close_df = pd.read_csv('Stock_data/Volume.csv', dtype={'date': str, 'CUSIP': str},
    #                         usecols=['date', 'VOL', 'CUSIP'])
    # volume_group = open_close_df.groupby('CUSIP')
    # print 'Start to split groups'
    # split_group = np.array_split(volume_group, process_num)
    # print "Use {} processors to do this part".format(process_num)
    # pool.map(process_split_group_volume_cusip, split_group)

    print 'Start to handle Compustat cusip'
    Compustat_df = pd.read_csv('Stock_data/Compustat.csv', dtype={'datadate': str, 'cusip': str})
    Compustat_df.loc[:, 'cusip'] = Compustat_df['cusip'].apply(lambda x: x[:-1])
    Compustat_group = Compustat_df.groupby('cusip')
    print 'Start to split groups'
    split_group = np.array_split(Compustat_group, process_num)
    print "Use {} processors to do this part".format(process_num)
    pool.map(process_split_compustat_cusip, split_group)
