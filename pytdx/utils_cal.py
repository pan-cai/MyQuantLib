#!/iQuant/MyQuantLib
# -*- coding: utf-8 -*-
# @Time    : 2018/2/21 23:23
# @Author  : Aries
# @Email   : aidabloc@163.com
# @File       : utils_cal.py

import tushare as ts
import pandas as pd
from datetime import timedelta
from datetime import datetime
from PyTdx.utils_function_timer import dy_func_timer


# 交易日历
START_DATE = '2009-01-01'
END_DATE = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')


class DyCal(object):
    def __init__(self, start=START_DATE, end=END_DATE):
        # tushare 交易日历
        # 日后替换其它数据源做交叉验证
        ts_cal = self.get_ts_cal(start, end)

        # 上证指数交易日历
        index_cal = self.get_index_cal(start, end)

        # 交叉验证交易日历
        self.cross_validation(ts_cal, index_cal)

        self.cal_date = index_cal.index.strftime("%Y-%m-%d")

    def __call__(self, *args, **kwargs):
        return self.cal_date

    @staticmethod
    @dy_func_timer
    def get_ts_cal(start_date, end_date):
        # 获取tushare 交易日历
        cal_date = ts.trade_cal()
        cal_date.set_index("calendarDate", inplace=True)
        cal_date.index = pd.to_datetime(cal_date.index)
        cal_date = cal_date.loc[start_date:end_date]
        return cal_date

    @staticmethod
    @dy_func_timer
    def get_index_cal(start_date, end_date):
        # 获取上证指数
        index_dates = ts.get_k_data(
            '000001', index=True, start=start_date, end=end_date)
        index_dates.set_index("date", inplace=True)
        index_dates["isOpen"] = int(1)
        index_dates = index_dates["isOpen"]
        index_dates.index = pd.to_datetime(index_dates.index)
        return index_dates

    @staticmethod
    @dy_func_timer
    def cross_validation(ts_cal, index_cal):
        # 交叉验证交易日历
        cross = pd.concat(
            [ts_cal.loc[ts_cal["isOpen"] == 1], index_cal], axis=1)
        cross.columns = ["cal", "index"]
        cross["cross"] = cross.iloc[:, 0] - cross.iloc[:, 1]
        cross["cross"].fillna(999)  # 针对可能存在的nan
        print("交易日历交叉验证:{}".format(cross["cross"].sum() == 0))
        print("交易日历{} : {}共{}个交易日".format(
            START_DATE, END_DATE, cross.shape[0]))


if __name__ == "__main__":
    cal = DyCal()()
    print(cal)



