#!/bin/bash

# python ./keep_alive.py &

python ./main.py &
python ./pic_bot.py &

# Wait for all process to exit
wait
