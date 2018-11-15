#!/bin/bash

#wget https://raw.githubusercontent.com/DonLakeFlyer/VHFCollarCompanion/master/rpi_setup.sh

echo "*** Install Bluetooth"
sudo apt-get install bluetooth bluez python-bluez blueman -y

echo "**  Install GNU Radio"
sudo apt-get install gnuradio -y

echo "*** Install OSX APF support"
sudo apt-get install netatalk -y

echo "*** Install tools for build Custom GNU Radio blocks"
sudo apt-get install cmake libairspy0 libairspy-dev swig -y

echo "*** Create repos directory"
cd ~
if [ ! -d repos ]; then
	mkdir repos
fi
cd ~/repos

echo "*** Install Airspy block"
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

echo "*** Install Pulse Sender block - UDP/BT"
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

echo "*** Install Pulse Detect block"
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

echo "*** Clone VHFCollarCompanion"
cd ~/repos
if [ ! -d VHFCollarCompanion ]; then
	git clone https://github.com/DonLakeFlyer/VHFCollarCompanion.git
fi

