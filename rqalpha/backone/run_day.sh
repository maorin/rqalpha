#!/bin/sh
# fetch data
rqalpha update_bundle
today=`date "+%Y%m%d"`
data_dir=data${today}
mkdir -p ${data_dir}/close_price
mkdir top500
mkdir merge_predicted_reslut

python fetch_all.py

# train LSTM
mkdir -p ${data_dir}/weight_json_day
mkdir -p ${data_dir}/weight_day

python lstm_train_all_by_day.py  ${today}
python predicted_next_day.py  ${today}

python recommender.py  ${today}
python merge_predicted_reslut.py  ${today}
python ga_select.py  ${today}


#back test


#sort

#send mail