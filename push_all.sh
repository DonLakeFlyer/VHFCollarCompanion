#!/bin/bash

echo "*** Push Airspy block"
cd ~/repos
if [ -d gr-airspysdr ]; then
	cd gr-airspysdr
	git push origin master
fi

echo "*** Push Pulse Sender block - UDP/BT"
cd ~/repos
if [ -d gr-VHFPulseSender ]; then
	cd gr-VHFPulseSender
	git push origin master
fi

echo "*** Push Pulse Detect block"
cd ~/repos
if [ -d gr-VHFPulseDetect ]; then
	cd gr-VHFPulseDetect
	git push origin master
fi

echo "*** Push VHFCollarCompanion"
cd ~/repos
if [ -d VHFCollarCompanion ]; then
	cd VHFCollarCompanion
	git push origin master
fi

