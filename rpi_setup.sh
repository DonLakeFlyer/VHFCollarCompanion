#!/bin/bash

# GRC Block setup is based on this discussion: https://lists.gnu.org/archive/html/discuss-gnuradio/2017-03/msg00083.html

#wget https://raw.githubusercontent.com/DonLakeFlyer/VHFCollarCompanion/master/rpi_setup.sh

echo "*** Install git"
sudo apt-get install git

echo "*** Clone VHFCollarCompanion"
cd ~/repos
if [ ! -d VHFCollarCompanion ]; then
	git clone https://github.com/DonLakeFlyer/VHFCollarCompanion.git
	cd VHFCollarCompanion
	git config credential.helper store
fi

echo "*** rPi Setup (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
	echo "*** Setup WiFi Connections"
	cd ~/repos/VHFCollarCompanion
	sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

	echo "*** Settings CPUs to performance mode"
	# https://github.com/DavidM42/rpi-cpu.gov
	# cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
	cd ~
	wget https://raw.githubusercontent.com/DavidM42/rpi-cpu.gov/master/install.sh && sudo chmod +x ./install.sh && sudo ./install.sh --nochown && sudo rm install.sh
	cpu.gov -g performance

	echo "**  Setup GRC Block Location"
	if [ -z ${GRC_HIER_PATH+x} ]; then 
		sudo sh -c 'echo "GRC_HIER_PATH=/home/pi/repos/VHFCollarCompanion" > /etc/environment'
	fi

	echo "*** Install OSX APF support"
	sudo apt-get install netatalk -y
else
	echo "**  Setup GRC Block Location"
	if [ -z ${GRC_HIER_PATH+x} ]; then 
		sudo sh -c 'echo "GRC_HIER_PATH=/home/parallels/repos/VHFCollarCompanion" > /etc/environment'
	fi	
fi

echo "*** VHF Drone setup (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
	sudo apt-get install python-pip -y
    sudo apt-get install libxml2-dev libxslt-dev python-dev
    sudo pip install -U pymavlink
    sudo pip install pyserial
fi

echo "**  Install GNU Radio"
sudo apt-get install gnuradio -y

echo "**  Install osmosdr block"
sudo apt-get install gr-osmosdr -y

echo "*** Install tools for build Custom GNU Radio blocks"
sudo apt-get install cmake libairspy0 libairspy-dev swig -y

echo "*** Create repos directory"
cd ~
if [ ! -d repos ]; then
	mkdir repos
fi
cd ~/repos

echo "*** Git setup"
git config --global user.email "don@thegagnes.com"
git config --global user.name "DonLakeFlyer"

echo "*** Install Pulse Sender block"
cd ~/repos
if [ ! -d gr-VHFPulseSender ]; then
	git clone https://github.com/DonLakeFlyer/gr-VHFPulseSender.git
	cd gr-VHFPulseSender
	git config credential.helper store
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
	git config credential.helper store
	mkdir build
	cd build/
	cmake ../
	make
	sudo make install
	sudo ldconfig
fi

cd ~/repos/VHFCollarCompanion