from __future__ import division, print_function
from ctypes import *
from libairspy import (
    libairspy,
    p_airspy_dev,
    airspy_sample_block_cb_fn,
)
import sys
import numpy as np
import logging

PY3 = sys.version_info.major >= 3
if PY3:
    basestring = str

class Airspy(object):
    # From airspy.h
    AIRSPY_SUCCESS = 0
    AIRSPY_TRUE = 1
    AIRSPY_ERROR_INVALID_PARAM = -2
    AIRSPY_ERROR_NOT_FOUND = -5
    AIRSPY_ERROR_BUSY = -6
    AIRSPY_ERROR_NO_MEM = -11
    AIRSPY_ERROR_LIBUSB = -1000
    AIRSPY_ERROR_THREAD = -1001
    AIRSPY_ERROR_STREAMING_THREAD_ERR = -1002
    AIRSPY_ERROR_STREAMING_STOPPED = -1003
    AIRSPY_ERROR_OTHER = -9999

    AIRSPY_SAMPLE_FLOAT32_IQ = 0    # 2 * 32bit float per sample
    AIRSPY_SAMPLE_FLOAT32_REAL = 1  # 1 * 32bit float per sample
    AIRSPY_SAMPLE_INT16_IQ = 2      # 2 * 16bit int per sample
    AIRSPY_SAMPLE_INT16_REAL = 3    # 1 * 16bit int per sample
    AIRSPY_SAMPLE_UINT16_REAL = 4   # 1 * 16bit unsigned int per sample
    AIRSPY_SAMPLE_RAW = 5           # Raw packed samples from the device
    AIRSPY_SAMPLE_END = 6           # Number of supported sample types

    # some default values for various parameters
    DEFAULT_GAIN = 'auto'
    DEFAULT_FC = 80e6
    DEFAULT_RS = 1.024e6
    DEFAULT_READ_SIZE = 1024

    CRYSTAL_FREQ = 28800000

    gain_values = []
    valid_gains_db = []
    buffer = []
    num_bytes_read = c_int32(0)
    device_opened = False

    def __init__(self, serial_number=None):
        self.open(serial_number)

    def open(self, device_index=0, test_mode_enabled=False, serial_number=None):
        self.dev_p = p_airspy_dev(None)

        result = libairspy.airspy_init()
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_init error: %s' % (self._airspyResultToString(result)))

        result = libairspy.airspy_open(self.dev_p)
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_open error: %s' % (self._airspyResultToString(result)))

        result = libairspy.airspy_set_samplerate(self.dev_p, 3000000)
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_sample_type error: %s ' % (self._airspyResultToString(result)))

        self.device_opened = True
        #self.init_device_values()

    def close(self):
        if not self.device_opened:
            return
        if self.dev_p:
            libairspy.airspy_close(self.dev_p)
            self.dev_p = p_airspy_dev(None)
        libairspy.airspy_exit()
        self.device_opened = False

    def __del__(self):
        self.close()

    def _airspyResultToString(self, result):
        return libairspy.airspy_error_name(result)

    def setFrequency(self, freq):
        freq = int(freq)
        self._freq = freq
        result = libairspy.airspy_set_freq(self.dev_p, freq)
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_freq error: %s ' % (self._airspyResultToString(result)))

    def _validGain(self, gain, minGain, maxGain):
        gain = int(gain)
        if gain < minGain:
            gain = minGain
        if gain > maxGain:
            gain = maxGain
        return gain

    def setLNAGain(self, gain):
        result = libairspy.airspy_set_lna_gain(self.dev_p, self._validGain(gain, 0, 15))
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_lna_gain error: %s ' % (self._airspyResultToString(result)))

    def setMixerGain(self, gain):
        result = libairspy.airspy_set_mixer_gain(self.dev_p, self._validGain(gain, 0, 15))
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_mixer_gain error: %s ' % (self._airspyResultToString(result)))

    def setVGAGain(self, gain):
        result = libairspy.airspy_set_vga_gain(self.dev_p, self._validGain(gain, 0, 15))
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_vga_gain error: %s ' % (self._airspyResultToString(result)))

    def _validEnabled(self, enabled):
        if enabled:
            return 1
        else:
            return 0

    def enableLNAAGC(self, enabled):
        result = libairspy.airspy_set_lna_agc(self.dev_p, self._validEnabled(enabled))
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_lna_agc error: %s ' % (self._airspyResultToString(result)))

    def enableMixerAGC(self, enabled):
        result = libairspy.airspy_set_mixer_agc(self.dev_p, self._validEnabled(enabled))
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_mixer_agc error: %s ' % (self._airspyResultToString(result)))

    def setLinearityGain(self, gain):
        result = libairspy.airspy_set_linearity_gain(self.dev_p, self._validGain(gain, 0, 21))
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_linearity_gain error: %s ' % (self._airspyResultToString(result)))

    def setSensitivityGain(self, gain):
        result = libairspy.airspy_set_sensitivity_gain(self.dev_p, self._validGain(gain, 0, 21))
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_sensitivity_gain error: %s ' % (self._airspyResultToString(result)))

    def enableBiasT(self, enabled):
        result = libairspy.airspy_set_rf_bias(self.dev_p, self._validEnabled(enabled))
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_set_rf_bias error: %s ' % (self._airspyResultToString(result)))

    def _rxCallback(self, airspyTransfer):
        #logging.debug("rxCallback %d %d", airspyTransfer.contents.sample_count, airspyTransfer.contents.dropped_samples)
        cFloats = airspyTransfer.contents.sample_count * 2
        array_type = (c_float*cFloats)
        values = cast(airspyTransfer.contents.samples, POINTER(array_type)).contents
        iq = np.empty(airspyTransfer.contents.sample_count, 'complex')
        iq.imag, iq.real = values[::2], values[1::2]
        self.rxCallback(iq)
        return 0

    def startReceive(self, rxCallback):
        self.rxCallback = rxCallback
        self.airspyCallback = airspy_sample_block_cb_fn(self._rxCallback)
        result = libairspy.airspy_start_rx(self.dev_p, self.airspyCallback, 0)
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_start_rx error: %s ' % (self._airspyResultToString(result)))

    def stopReceive(self):
        result = libairspy.airspy_stop_rx(self.dev_p)
        if result != Airspy.AIRSPY_SUCCESS:
            raise IOError('airspy_start_rx error: %s ' % (self._airspyResultToString(result)))

    def isStreaming(self):
        return libairspy.airspy_is_streaming(self.dev_p)
