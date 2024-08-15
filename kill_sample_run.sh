#!/bin/bash

ps -ef | grep 'python server.py' | grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep 'python train.py' | grep -v grep | awk '{print $2}' | xargs kill