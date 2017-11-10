import time
import logging

from rtlsdr import RtlSdr
from matplotlib.mlab import magnitude_spectrum, psd
from multiprocessing import Process
from queue import Queue
from scipy.signal import decimate

NFFT = 64
NUM_SAMPLES_PER_SCAN = 1024 # NFFT * 16

class PulseDetector(Process):
    def __init__(self, sampleQueue, setFreqQueue, setGainQueue):
        Process.__init__(self)
        self.sampleQueue = sampleQueue
        self.setFreqQueue = setFreqQueue
        self.setGainQueue = setGainQueue

    def run(self):
        logging.debug("PulseDetector.run")
        try:
            sdr = RtlSdr()
            sdr.rs = 2.4e6
            sdr.fc = 146e6
            sdr.gain = 25
        except Exception as e:
            logging.exception("SDR init failed")
            return

        while True:
            try:
                newFrequency = self.setFreqQueue.get_nowait()
            except Exception as e:
                pass
            else:
                logging.debug("Changing frequency %d", newFrequency)
                sdr.fc = newFrequency
            try:
                newGain = self.setGainQueue.get_nowait()
            except Exception as e:
                pass
            else:
                sdr.gain = newGain
                logging.debug("Changing gain %d:%d", newGain, sdr.gain)
            sdrReopen = False
            try:
                samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
            except Exception as e:
                logging.exception("SDR read failed")
                sdrReopen = True
            if sdrReopen:
                logging.debug("Attempting reopen")
                try:
                    sdr.open()
                except Exception as e:
                    logging.exception("SDR reopen failed")
                    return
                try:
                    samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)
                except Exception as e:
                    logging.exception("SDR read failed")
                    return
            self.sampleQueue.put(samples)