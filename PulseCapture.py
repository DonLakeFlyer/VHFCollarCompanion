import time
import logging
import os
import csv

from multiprocessing import Process
from queue import Queue

NFFT = 64
NUM_SAMPLES_PER_SCAN = 1024 # NFFT * 16

class PulseCapture(Process):
    def __init__(self, tools):
        Process.__init__(self)
        self.pulseQueue = tools.pulseQueue
        self.setFreqQueue = tools.setFreqQueue
        self.setGainQueue = tools.setGainQueue
        self.setAmpQueue = tools.setAmpQueue
        self.workDir = tools.workDir
        self.pyDir = tools.pyDir
        self.freq = 146
        self.gain = 21
        self.amp = False

    def processFreqQueue(self):
        try:
            self.freq = self.setFreqQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing frequency %f", self.freq)

    def processGainQueue(self):
        try:
            self.gain = self.setGainQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing gain %d", self.gain)

    def processAmpQueue(self):
        try:
            self.amp = self.setAmpQueue.get_nowait()
        except Exception as e:
            pass
        else:
            logging.debug("Changing amp %s", self.amp)

    def run(self):
        logging.debug("PulseCapture.run")

        while True:
            self.processFreqQueue()
            self.processGainQueue()
            self.processAmpQueue()

            #os.remove("values.dat")
            #os.remove("pulse.dat")

            # Capture 3 seconds worth of data
            commandStr = "airspy_rx -r " + self.workDir + "/values.dat -f {0} -a 3000000 -h {1}  -n 9000000"
            command = commandStr.format(self.freq, self.gain)
            ret = os.system(command)
            print(ret)
            if ret == 256:
                logging.debug("airspy_rx returned error %d", ret)
                break

            # Process raw data for pulses
            os.system("/usr/bin/python3 " + self.pyDir + "/AirspyProcessData.py --noCSV --workDir " + self.workDir)

            # Read the processed data and send pulse average if available
            rgPulse = []
            with open(self.workDir + "/pulse.dat") as csvfile:
                print("Here")
                reader = csv.reader(csvfile)
                for row in reader:
                    rgPulse.append(float(row[0]))
                if len(rgPulse) > 0:
                    pulseAvg = sum(rgPulse) / len(rgPulse)
                    # Change to range of 0 - 100
                    pulseAvg = int((pulseAvg / 300000.0) * 100.0)
                else:
                    pulseAvg = 0
                logging.debug("***** %d %d pulseAvg:len(rgPulse)", pulseAvg, len(rgPulse))
                if self.pulseQueue:
                    self.pulseQueue.put(pulseAvg)
