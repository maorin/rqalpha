# coding: utf-8

from rqalpha.api import *
import talib
from rqalpha import run_func
import numpy as np
import pandas as pd
import datetime
import os
from keras.models import load_model,model_from_json
from keras import backend as K
from numpy import newaxis
import shutil
import time
"""
Bar(symbol: u'\u73e0\u6c5f\u94a2\u7434', order_book_id: u'002678.XSHE', datetime: datetime.datetime(2014, 1, 2, 0, 0), 
open: 7.08, close: 7.07, high: 7.14, low: 7.03, volume: 3352317.0, total_turnover: 23756852, limit_up: 7.78, limit_down: 6.36)

total_turnover  资产周转率
volume 成交量

"""


    
# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init_dl(context):
    # 在context中保存全局变量
    context.s1 = context.config.stock_id
    context.predicted_one = context.config.predicted_one
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
    
    
    if  context.predicted_one:
        context.all = [context.s1]
    
    result = {}
    for s1 in context.all:
        logger.info("----------22222-------%s-------" % bar_dict[s1])
        order_book_id = s1
        global_start_time = time.time()
        history_close = history_bars(order_book_id, 51, '1d', 'close')
        history_close = history_close[:-1]
        if len(history_close) != 50:
            continue
        if not os.path.isfile('weight_week/%s.npy.h5' % order_book_id):
            continue
        if not os.path.isfile('weight_json_week/%s.npy.h5' % order_book_id):
            continue
        
        y = bar_dict[order_book_id].close
        
        yesterday_close = history_close[-1]
        normalised_history_close = [((float(p) / float(history_close[0])) - 1) for p in history_close]
        print "history_close: %s" % history_close
        print "normalised_history_close: %s" % normalised_history_close
        normalised_yesterday_close = normalised_history_close[-1]
        
        normalised_history_close = np.array(normalised_history_close)
        normalised_history_close = normalised_history_close[newaxis,:]
        normalised_history_close = normalised_history_close[:,:,newaxis]
        


        json_file = open("weight_json_week/%s.npy.h5"% order_book_id, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights("weight_week/%s.npy.h5" % order_book_id) 
        
        
        #model = load_model('model/%s.h5' % order_book_id)
        #model.compile(loss="mse", optimizer="rmsprop")
        predicted = model.predict(normalised_history_close)[0,0]
        del model
        K.clear_session()
        normalised_history_close = [((float(p) / float(history_close[0])) - 1) for p in history_close]
        normalised_history_close.append(predicted)
        restore_normalise_window = [float(history_close[0]) * (float(p) + 1) for p in normalised_history_close]
        
        restore_predicted = restore_normalise_window[-1]
        
        if restore_predicted > yesterday_close:
            inc = round(round(restore_predicted-yesterday_close, 2)  /  yesterday_close, 2)
            logger.info("predicted: %s yesterday_close:%s restore_predicted:%s real: %s" %  (predicted,yesterday_close, restore_predicted, y))
            filename =  "%s.npy.h5" % order_book_id
    
            result[filename] = {"stock_id":order_book_id,
                                "normalised_yesterday_close":normalised_yesterday_close, 
                                "yesterday_close": yesterday_close, 
                                "predicted":predicted, 
                                "restore_predicted": restore_predicted, 
                                "inc": inc}
    
    print result
    df = pd.DataFrame(pd.DataFrame(result).to_dict("index"))
    print df
    today = datetime.date.today().strftime("%Y-%m-%d")
    df.to_csv ("predicted_result%s.csv" % today, encoding="utf-8")

        
# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading_dl(context):
    logger.info("收盘后执行after_trading函数")



before_yesterday = (datetime.date.today() -  datetime.timedelta(days=2)).strftime("%Y-%m-%d")
yesterday = (datetime.date.today() -  datetime.timedelta(days=1)).strftime("%Y-%m-%d")
print before_yesterday
print yesterday
config_dl = {
  "stock_id":"002698.XSHE",
  "predicted_one":False,
  "base": {
    "start_date": before_yesterday,
    "end_date": yesterday,
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
run_func(init=init_dl, before_trading=before_trading_dl, handle_bar=handle_bar_dl, config=config_dl)
