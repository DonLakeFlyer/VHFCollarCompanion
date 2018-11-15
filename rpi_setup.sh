#!/bin/bash

#wget https://raw.githubusercontent.com/DonLakeFlyer/VHFCollarCompanion/master/rpi_setup.sh

echo "*** Install Bluetooth (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
	echo "*** Installing Bluetooth packages"
	sudo apt-get install bluetooth bluez python-bluez blueman expect -y
	# Fixed screwed up bluez install
	# https://raspberrypi.stackexchange.com/questions/41776/failed-to-connect-to-sdp-server-on-ffffff000000-no-such-file-or-directory
	echo "*** Fixing bluez sdp problem"
	sed 's|ExecStart=/usr/lib/bluetooth/bluetoothd|ExecStart=/usr/lib/bluetooth/bluetoothd -C\nExecStartPost=/bin/chmod 777 /var/run/sdp|' /etc/systemd/system/dbus-org.bluez.service >fixed.service
	cp fixed.service /etc/systemd/system/dbus-org.bluez.service
	rm fixed.service
	sudo systemctl daemon-reload
	sudo systemctl restart bluetooth
	echo "*** Making bluetooth discoverable"
	wget https://raw.githubusercontent.com/DonLakeFlyer/VHFCollarCompanion/master/bluetoothctl.sh
	chmod +x bluetoothctl.sh
	./bluetoothctl.sh
	rm bluetoothctl.sh
fi

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

echo "*** Git setup"
git config --global user.email "don@thegagnes.com"
git config --global user.name "DonLakeFlyer"

echo "*** Install Airspy block"
cd ~/repos
if [ ! -d gr-airspysdr ]; then
	git clone https://github.com/DonLakeFlyer/gr-airspysdr.git
	cd gr-airspysdr
	git config credential.helper store
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

