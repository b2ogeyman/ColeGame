#!/bin/zsh

for i in {1..100}
do
	python3 MCColeGame.py --logfile ./line_vs_angle.txt --first bot_line --second bot_angle --noprint --num 10 > /dev/null 
	echo $i
done

#24%