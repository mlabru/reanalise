#!/bin/bash

# language
# export LANGUAGE=pt_BR

# reanalise directory
REANALISE=~/reanalise/srce

# nome do computador
HOST=`hostname`

# get today's date
TDATE=`date '+%Y-%m-%d_%H-%M-%S'`

# home directory exists ?
if [ -d ${REANALISE} ]; then
    # set home dir
    cd ${REANALISE}
fi

# ckeck if another instance of downloader is running
DI_PID_DOWN=`ps ax | grep -w python3 | grep -w rea_download.py | awk '{ print $1 }'`

if [ ! -z "$DI_PID_DOWN" ]; then
    # log warning
    echo "[`date`]: process download is already running. Waiting..." >> $LOGF
    # kill process
    kill -9 $DI_PID_DOWN
    # wait 10s
    sleep 10
fi

# set PYTHONPATH
export PYTHONPATH="$PWD/."

# executa o downloader
python3 rea_download.py $@ >> logs/rea_download.$HOST.$TDATE.log 2>&1
# executa a reanalise
python3 reanalise.py $@ >> logs/reanalise.$HOST.$TDATE.log 2>&1

# logger
echo "Fim de processamento: " $(date '+%Y-%m-%d %H:%M') >> logs/rea.$HOST.$TDATE.log

# < the end >---------------------------------------------------------------------------
