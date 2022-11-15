#!/bin/bash

# python ./keep_alive.py &

python ./main.py &
bg &
python ./pic_bot.py &
bg &

# Wait for all process to exit
wait
