#!/bin/bash

echo "************** Update VHFCollarCompanion"
cd ~/repos
if [ -d VHFCollarCompanion ]; then
	cd VHFCollarCompanion
	git fetch origin master
	git reset --hard origin/master
fi

cd ~/repos/VHFCollarCompanion
source update_all_2.sh
