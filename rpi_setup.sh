#!/bin/bash

# GRC Block setup is based on this discussion: https://lists.gnu.org/archive/html/discuss-gnuradio/2017-03/msg00083.html

#wget https://raw.githubusercontent.com/DonLakeFlyer/VHFCollarCompanion/master/rpi_setup.sh

echo "*** Install Bluetooth (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
	echo "*** Installing Bluetooth packages"
	sudo apt-get install bluetooth bluez python-bluez blueman expect -y
	# Fixed screwed up bluez install
	# https://raspberrypi.stackexchange.com/questions/41776/failed-to-connect-to-sdp-server-on-ffffff000000-no-such-file-or-directory
	echo "*** Fixing bluez sdp problem"
	sed 's|^ExecStart=/usr/lib/bluetooth/bluetoothd$|ExecStart=/usr/lib/bluetooth/bluetoothd -C\nExecStartPost=/bin/chmod 777 /var/run/sdp|' /etc/systemd/system/dbus-org.bluez.service >fixed.service
	sudo cp fixed.service /etc/systemd/system/dbus-org.bluez.service
	rm fixed.service
	sudo systemctl daemon-reload
	sudo systemctl restart bluetooth
fi

echo "**  Install GNU Radio"
sudo apt-get install gnuradio -y

echo "**  Setup GRC Block Location"
if [ -z ${GRC_HIER_PATH+x} ]; then 
	sudo sh -c 'echo "GRC_HIER_PATH=/home/pi/repos/VHFCollarCompanion" > /etc/environment'
fi

echo "*** UnInstall Deprecated Airspy block"
cd ~/repos
if [ -d gr-airspysdr ]; then
	cd gr-airspysdr/build
	sudo make uninstall
	sudo ldconfig
fi

echo "**  Install osmosdr block"
sudo apt-get install gr-osmosdr -y

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

echo "*** Git setup"
git config --global user.email "don@thegagnes.com"
git config --global user.name "DonLakeFlyer"

echo "*** Install Pulse Sender block - UDP/BT"
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

echo "*** Clone VHFCollarCompanion"
cd ~/repos
if [ ! -d VHFCollarCompanion ]; then
	git clone https://github.com/DonLakeFlyer/VHFCollarCompanion.git
	cd VHFCollarCompanion
	git config credential.helper store
fi

echo "*** Settings CPUs to performance mode"
# https://github.com/DavidM42/rpi-cpu.gov
cd ~
wget https://raw.githubusercontent.com/DavidM42/rpi-cpu.gov/master/install.sh && sudo chmod +x ./install.sh && sudo ./install.sh --nochown && sudo rm install.sh
cpu.gov -g performance

cd ~/repos/VHFCollarCompanion