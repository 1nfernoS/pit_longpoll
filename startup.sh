#!/bin/bash

python ./main.py &
bg &
python ./pic_bot.py &
bg &

# Wait for all process to exit
wait
