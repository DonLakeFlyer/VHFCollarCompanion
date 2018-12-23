#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Pulsedetectfactorsgui
# Generated: Sat Dec 22 17:36:32 2018
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PulseDetectBase import PulseDetectBase  # grc-generated hier_block
from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import VHFPulseDetect
import VHFPulseSender
import cmath
import math
import sip


class PulseDetectFactorsGui(gr.top_block, Qt.QWidget):

    def __init__(self, pulse_freq=146e6, samp_rate=3e6):
        gr.top_block.__init__(self, "Pulsedetectfactorsgui")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Pulsedetectfactorsgui")
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "PulseDetectFactorsGui")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Parameters
        ##################################################
        self.pulse_freq = pulse_freq
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.total_decimation = total_decimation = 16*8*8
        self.wnT = wnT = math.pi/4.0*0+0.635
        self.threshold = threshold = 2.5
        self.minSamplesForPulse = minSamplesForPulse = 130
        self.gain = gain = 21
        self.final_samp_rate = final_samp_rate = samp_rate/total_decimation

        ##################################################
        # Blocks
        ##################################################
        self._wnT_range = Range(0.001, math.pi, 0.001, math.pi/4.0*0+0.635, 200)
        self._wnT_win = RangeWidget(self._wnT_range, self.set_wnT, "PLL Loop BW", "counter_slider", float)
        self.top_grid_layout.addWidget(self._wnT_win, 3,0,1,1)
        self._threshold_range = Range(1.0, 10.0, 0.1, 2.5, 200)
        self._threshold_win = RangeWidget(self._threshold_range, self.set_threshold, "Threshold", "counter_slider", float)
        self.top_grid_layout.addWidget(self._threshold_win, 1,0,1,1)
        self._minSamplesForPulse_range = Range(10, 300, 1, 130, 200)
        self._minSamplesForPulse_win = RangeWidget(self._minSamplesForPulse_range, self.set_minSamplesForPulse, "Min samples for pulse", "counter_slider", int)
        self.top_grid_layout.addWidget(self._minSamplesForPulse_win, 2,0,1,1)
        self._gain_range = Range(0, 21, 1, 21, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, "Gain", "counter_slider", int)
        self.top_grid_layout.addWidget(self._gain_win, 0,0,1,1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
        	int(final_samp_rate*10.0), #size
        	final_samp_rate, #samp_rate
        	"Pulse Processing Views", #name
        	6 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)
        
        self.qtgui_time_sink_x_0.set_y_label("Amplitude", "")
        
        self.qtgui_time_sink_x_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        
        if not True:
          self.qtgui_time_sink_x_0.disable_legend()
        
        labels = ["Pulse Detect", "Pulse Raw", "Moving Avg", "Moving Var", "Moving StdDev",
                  "Threshold", "Re{Ref Out}", "Im{Ref Out}", "Ref Frequency", "zero"]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "magenta",
                  "cyan", "dark green", "dark red", "Dark Blue", "Dark Blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 3, 0]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        
        for i in xrange(6):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 4,0,1,1)
        self.blocks_vector_sink_x_0 = blocks.vector_sink_c(1)
        self.VHFPulseSender_udp_sender_f_0 = VHFPulseSender.udp_sender_f()
        self.VHFPulseDetect_pulse_detect__ff_0 = VHFPulseDetect.pulse_detect__ff(threshold, minSamplesForPulse)
        self.PulseDetectBase = PulseDetectBase(
            freq_shift=0,
            gain=gain,
            wnT=wnT,
            pulse_freq=pulse_freq,
            samp_rate=samp_rate,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.PulseDetectBase, 0), (self.VHFPulseDetect_pulse_detect__ff_0, 0))    
        self.connect((self.PulseDetectBase, 1), (self.blocks_vector_sink_x_0, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 0), (self.VHFPulseSender_udp_sender_f_0, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 2), (self.qtgui_time_sink_x_0, 2))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 4), (self.qtgui_time_sink_x_0, 4))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 3), (self.qtgui_time_sink_x_0, 3))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 1), (self.qtgui_time_sink_x_0, 1))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 0), (self.qtgui_time_sink_x_0, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 5), (self.qtgui_time_sink_x_0, 5))    

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "PulseDetectFactorsGui")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


    def get_pulse_freq(self):
        return self.pulse_freq

    def set_pulse_freq(self, pulse_freq):
        self.pulse_freq = pulse_freq
        self.PulseDetectBase.set_pulse_freq(self.pulse_freq)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_final_samp_rate(self.samp_rate/self.total_decimation)
        self.PulseDetectBase.set_samp_rate(self.samp_rate)

    def get_total_decimation(self):
        return self.total_decimation

    def set_total_decimation(self, total_decimation):
        self.total_decimation = total_decimation
        self.set_final_samp_rate(self.samp_rate/self.total_decimation)

    def get_wnT(self):
        return self.wnT

    def set_wnT(self, wnT):
        self.wnT = wnT
        self.PulseDetectBase.set_wnT(self.wnT)

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.VHFPulseDetect_pulse_detect__ff_0.set_threshold(self.threshold)

    def get_minSamplesForPulse(self):
        return self.minSamplesForPulse

    def set_minSamplesForPulse(self, minSamplesForPulse):
        self.minSamplesForPulse = minSamplesForPulse
        self.VHFPulseDetect_pulse_detect__ff_0.set_minSamplesForPulse(self.minSamplesForPulse)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.PulseDetectBase.set_gain(self.gain)

    def get_final_samp_rate(self):
        return self.final_samp_rate

    def set_final_samp_rate(self, final_samp_rate):
        self.final_samp_rate = final_samp_rate
        self.qtgui_time_sink_x_0.set_samp_rate(self.final_samp_rate)


def argument_parser():
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option(
        "", "--pulse-freq", dest="pulse_freq", type="eng_float", default=eng_notation.num_to_str(146e6),
        help="Set pulse_freq [default=%default]")
    parser.add_option(
        "", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(3e6),
        help="Set samp_rate [default=%default]")
    return parser


def main(top_block_cls=PulseDetectFactorsGui, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(pulse_freq=options.pulse_freq, samp_rate=options.samp_rate)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
