#!/bin/zsh

for i in {1..100}
do
	python3 MCColeGame.py --logfile ./angle_vs_line.txt --first bot_angle --second bot_line --noprint --num 10 > /dev/null 
	echo $i
done