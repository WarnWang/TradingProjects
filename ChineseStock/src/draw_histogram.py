#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Filename: draw_histogram
# @Date: 2017-02-09
# @Author: Mark Wang
# @Email: wangyouan@gmial.com

import os
import re

import pandas as pd

from util_functions.os_related import get_target_file_name
from util_functions.util_function import plot_picture, draw_histogram, get_max_draw_down, get_sharpe_ratio, get_annualized_return
from constants import Constant as const

# result_path = '/home/zigan/Documents/WangYouan/trading/ChineseStock/result/si_own_cd_insider'
result_path = '/Users/warn/PycharmProjects/QuestionFromProfWang/ChineseStock/result/all_report_new_date'


def draw_wealth_pictures(wealth_result, picture_save_path, method_name, save_name,
                         stop_loss_rate, statistics_df=None):
    pic_path = picture_save_path

    if statistics_df is None:
        sharpe_ratio = get_sharpe_ratio(wealth_result, df_type=const.WEALTH_DATAFRAME)[method_name]
        ann_return = get_annualized_return(wealth_result, df_type=const.WEALTH_DATAFRAME)[method_name]
    else:
        sharpe_ratio = statistics_df.ix['sharpe_ratio', method_name]
        ann_return = statistics_df.ix['annualized_return', method_name]

    max_draw_down = get_max_draw_down(wealth_result[method_name])
    text = 'Sharpe ratio: {:.3f}, Annualized return: {:.2f}%'.format(sharpe_ratio,
                                                                     ann_return * 100)

    text = '{}, Max drawdown rate: {:.2f}%, SR: {}%'.format(text, max_draw_down * 100,
                                                            stop_loss_rate)
    text = '{}, Transaction cost: 0.2%'.format(text)
    plot_picture(wealth_result[method_name], method_name, os.path.join(pic_path, '{}.png'.format(save_name)), text)


if __name__ == '__main__':
    best_sharpe_ratio = 0.0
    best_sharpe_ratio_wealth = None
    best_sharpe_ratio_name = None
    best_sharpe_ratio_sr_rate = None
    best_ann_return = 0.0
    best_ann_return_wealth = None
    best_ann_return_name = None
    best_ann_return_sr_rate = None

    statistics_df_list = []

    dir_list = os.listdir(result_path)

    # vdisplay = Xvfb(width=1366, height=768)
    # vdisplay.start()

    for dir_name in dir_list:
        current_path = os.path.join(result_path, dir_name)
        if not os.path.isdir(current_path):
            continue

        statistics_file_name = get_target_file_name(current_path, 'statistic', 'p')
        wealth_file_name = get_target_file_name(current_path, 'sr', 'p')

        if wealth_file_name is None:
            wealth_file_name = get_target_file_name(current_path, 'stoploss', 'p')

        if statistics_file_name is None or wealth_file_name is None:
            continue

        statistics_df = pd.read_pickle(os.path.join(current_path, statistics_file_name))
        statistics_df_t = statistics_df.transpose()
        statistics_df_list.append(statistics_df_t)

        wealth_df = pd.read_pickle(os.path.join(current_path, wealth_file_name))

        draw_histogram(statistics_df_t['sharpe_ratio'], 'Sharpe Ratio', 'Strategies', 'Histogram of Sharpe Ratio',
                       os.path.join(current_path, 'sharpe_ratio_histogram.png'))

        draw_histogram(statistics_df_t['annualized_return'], 'Annualized Return', 'Strategies',
                       'Histogram of Annualized Return',
                       os.path.join(current_path, 'ann_return_histogram.png'))

        stop_loss_rate = re.findall(r'\d+', wealth_file_name)[-1]

        best_sharpe_name = statistics_df_t.sharpe_ratio.idxmax()
        best_annualized_return_name = statistics_df_t.annualized_return.idxmax()
        draw_wealth_pictures(wealth_df, statistics_df=statistics_df, picture_save_path=current_path,
                             method_name=best_sharpe_name,
                             save_name='best_sharpe_ratio', stop_loss_rate=stop_loss_rate)
        draw_wealth_pictures(wealth_df, statistics_df=statistics_df, picture_save_path=current_path,
                             method_name=best_annualized_return_name,
                             save_name='best_ann_return', stop_loss_rate=stop_loss_rate)
        if statistics_df.ix['annualized_return', best_annualized_return_name] > best_ann_return:
            best_ann_return = statistics_df.ix['annualized_return', best_annualized_return_name]
            best_ann_return_wealth = wealth_df
            best_ann_return_name = best_annualized_return_name
            best_ann_return_sr_rate = stop_loss_rate

        if statistics_df.ix['sharpe_ratio', best_sharpe_name] > best_sharpe_ratio:
            best_sharpe_ratio = statistics_df.ix['sharpe_ratio', best_sharpe_name]
            best_sharpe_ratio_wealth = wealth_df
            best_sharpe_ratio_name = best_sharpe_name
            best_sharpe_ratio_sr_rate = stop_loss_rate

    if best_sharpe_ratio_wealth is not None:
        draw_wealth_pictures(best_sharpe_ratio_wealth, picture_save_path=result_path,
                             method_name=best_sharpe_ratio_name, save_name='best_sharpe',
                             stop_loss_rate=best_sharpe_ratio_sr_rate)

    if best_ann_return_name is not None:
        draw_wealth_pictures(best_ann_return_wealth, picture_save_path=result_path,
                             method_name=best_ann_return_name, save_name='best_ann_return',
                             stop_loss_rate=best_ann_return_sr_rate)

    merged_sta_df = pd.concat(statistics_df_list, axis=0, ignore_index=False)

    draw_histogram(merged_sta_df['sharpe_ratio'], 'Sharpe Ratio', 'Strategies', 'Histogram of Sharpe Ratio',
                   os.path.join(result_path, 'sharpe_ratio_histogram.png'))

    draw_histogram(merged_sta_df['annualized_return'], 'Annualized Return', 'Strategies',
                   'Histogram of Annualized Return',
                   os.path.join(result_path, 'ann_return_histogram.png'))

    # vdisplay.stop()
