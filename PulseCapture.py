import time
import logging
import subprocess
import csv
import AirspyProcessData

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

            sampleRate = 3000000
            sampleCount = 9000000
            biasTee = 1
            ifGain = 5
            mixerGain = 15
            lnaGain = 0


            # Capture 3 seconds worth of data
            airspyArgs = [ "airspy_rx", 
                            "-r ", self.workDir + "/values.dat", 
                            "-f", str(self.freq), 
                            "-a", str(sampleRate),
                            "-v", str(ifGain), 
                            "-m", str(mixerGain), 
                            "-l", str(lnaGain), 
                            "-b", str(biasTee), 
                            #"-h", str(self.gain), 
                            "-n", str(sampleCount) ]
            try:
#                subprocess.check_output(airspyArgs, stderr=subprocess.STDOUT, universal_newlines=True)
                subprocess.check_output(airspyArgs, universal_newlines=True)
            except subprocess.CalledProcessError as e:
                logging.debug("airspy_rx failed")
                logging.debug(e.output)
                return

            # Process raw data for pulses
            AirspyProcessData.processValuesFile(self.workDir, True)

            # Read the processed data and send pulse average if available
            rgPulse = []
            with open(self.workDir + "/pulse.dat") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    rgPulse.append(float(row[0]))
                if len(rgPulse) > 0:
                    maxPulse = 2000000
                    pulseMax = min(max(rgPulse), maxPulse)
                    # Change to range of 0 - 100
                    pulseMax = int((pulseMax / maxPulse) * 100.0)
                else:

                    pulseMax = 0
                logging.debug("***** %d %d pulseMax:len(rgPulse)", pulseMax, len(rgPulse))
                if self.pulseQueue:
                    self.pulseQueue.put(pulseMax)
