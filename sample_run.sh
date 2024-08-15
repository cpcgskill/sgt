#!/bin/bash

# create log dir, if not exists
if [ ! -d "sgt_log" ]; then
    mkdir sgt_log
fi

#
nohup ./_sample_run.sh python server.py > "sgt_log/server.log" &
for (( i=1; i<=6; i++ ))
do
   nohup ./_sample_run.sh python train.py > "sgt_log/train_$i.log" &
done