#!/bin/bash

echo "************** Update Pulse Sender block - UDP/BT"
cd ~/repos
if [ -d gr-VHFPulseSender ]; then
	cd gr-VHFPulseSender
	git pull origin master
	cd build/
    make clean
	make
	sudo make install
	sudo ldconfig
fi

echo "************** Install Pulse Detect block"
cd ~/repos
if [ -d gr-VHFPulseDetect ]; then
	cd gr-VHFPulseDetect
	git pull origin master
	cd build/
    make clean
	make
	sudo make install
	sudo ldconfig
fi
