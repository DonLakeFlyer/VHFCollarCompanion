#!/bin/bash

echo "************** Update Airspy block"
cd ~/repos
if [ -d gr-airspysdr ]; then
	cd gr-airspysdr
	git pull origin master
	cd build/
    make clean
	make
	sudo make install
	sudo ldconfig
fi

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

echo "************** Update VHFCollarCompanion"
cd ~/repos
if [ -d VHFCollarCompanion ]; then
	cd VHFCollarCompanion
	git pull origin master
fi

