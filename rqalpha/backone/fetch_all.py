# coding: utf-8

from rqalpha.api import *
from rqalpha import run_func
import numpy as np
import pandas as pd
import datetime
import os, sys
import shutil
"""
Bar(symbol: u'\u73e0\u6c5f\u94a2\u7434', order_book_id: u'002678.XSHE', datetime: datetime.datetime(2014, 1, 2, 0, 0), 
open: 7.08, close: 7.07, high: 7.14, low: 7.03, volume: 3352317.0, total_turnover: 23756852, limit_up: 7.78, limit_down: 6.36)

total_turnover  资产周转率
volume 成交量

"""
print len(sys.argv)
if len(sys.argv) == 2:
    today = sys.argv[1]
    now_time = datetime.datetime.strptime(today, "%Y%m%d")
    yesterday =  (now_time + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")    
    

else:
    today = datetime.date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() -  datetime.timedelta(days=1)).strftime("%Y-%m-%d")

print yesterday


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init_dl(context):
    # 在context中保存全局变量
    context.s1 = context.config.stock_id
    context.config
    context.all_close_price = {}
    context.today = None
    
    logger.info("RunInfo: {}".format(context.run_info))
    df = (all_instruments('CS'))
    context.all = df["order_book_id"]
    
# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading_dl(context):
    logger.info("开盘前执行before_trading函数")

# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar_dl(context, bar_dict):
    logger.info("每一个Bar执行")
    logger.info("打印Bar数据：")
    
    for s1 in context.all:

        order_book_id = bar_dict[s1].order_book_id
        history_close = history_bars(order_book_id, 10000, '1d', 'close')


        context.all_close_price[order_book_id] = history_close
    
    if os.path.exists("close_price"):
        shutil.rmtree("close_price")
    os.mkdir("close_price")
    
    #if not os.path.exists("close_price"):

    for book_id, data in context.all_close_price.items():
        print book_id
        print data
        print today
        np.save("close_price/%s" % book_id, data)
        #today = datetime.date.today().strftime("%Y%m%d")
        np.save("data%s/close_price/%s" % (today, book_id), data)
        
        #df = pd.DataFrame(data)
        #df.save("close_price/%s" % book_id,  encoding = "utf-8")   
   
        
# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading_dl(context):
    logger.info("收盘后执行after_trading函数")






config_dl = {
  "stock_id":"000001.XSHE",
  "base": {
    "start_date": yesterday,
    "end_date": today,
    "accounts": {
        "stock": 100000
    }
  },
  "extra": {
    "log_level": "verbose",
  },
  "mod": {
    "sys_analyser": {
      "enabled": True,
      "plot": False
    }
  }
}

# 您可以指定您要传递的参数
run_func(init=init_dl, before_trading=before_trading_dl, handle_bar=handle_bar_dl,  config=config_dl)
