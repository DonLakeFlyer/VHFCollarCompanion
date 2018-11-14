#!/bin/bash

#wget https://raw.githubusercontent.com/DonLakeFlyer/VHFCollarCompanion/master/rpi_setup.sh

# Bluetooth
sudo apt-get install bluetooth bluez python-bluez blueman -y

# GNU Radio Install
sudo apt-get install gnuradio -y

# Support for open file system from OSX
sudo apt-get install netatalk -y

# Custom GNU Radio Blocks
sudo apt-get install cmake libairspy0 libairspy-dev swig -y

# Setup for repos
cd ~
if [ ! -d repos ]; then
	mkdir repos
fi
cd ~/repos

# Airspy block
cd ~/repos
if [ ! -d gr-airspysdr ]; then
	git clone https://github.com/DonLakeFlyer/gr-airspysdr.git
	cd gr-airspysdr
	mkdir build
	cd build/
	cmake ../ -DENABLE_RTL=OFF -DENABLE_REDPITAYA=OFF -DENABLE_RFSPACE=OFF -DENABLE_RTL_TCP=OFF -DENABLE_FCD=OFF -DENABLE_FCDPP=OFF
	make
	sudo make install
	sudo ldconfig
fi

# Pulse Sender block - UDP/BT
cd ~/repos
if [ ! -d gr-VHFPulseSender ]; then
	git clone https://github.com/DonLakeFlyer/gr-VHFPulseSender.git
	cd gr-VHFPulseSender
	mkdir build
	cd build/
	cmake ../
	make
	sudo make install
	sudo ldconfig
fi

# Pulse Detect block
cd ~/repos
if [ ! -d gr-VHFPulseDetect ]; then
	git clone https://github.com/DonLakeFlyer/gr-VHFPulseDetect.git
	cd gr-VHFPulseDetect
	mkdir build
	cd build/
	cmake ../
	make
	sudo make install
	sudo ldconfig
fi

cd ~/repos
if [ ! -d VHFCollarCompanion ]; then
	git clone https://github.com/DonLakeFlyer/VHFCollarCompanion.git
fi

