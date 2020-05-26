#!/bin/zsh

for i in {1..10}
do
	python3 MCColeGame.py --logfile ./angle_vs_line_10.txt --first botmc_angle --second botmc_line --noprint --r1 2000 --r2 2000 > /dev/null 
	echo $i
done