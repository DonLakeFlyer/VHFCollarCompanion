#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Pulsedetectgui
# Generated: Fri Jul  6 15:05:30 2018
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
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import cmath
import math
import sip


class PulseDetectGUI(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Pulsedetectgui")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Pulsedetectgui")
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

        self.settings = Qt.QSettings("GNU Radio", "PulseDetectGUI")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.total_decimation = total_decimation = 4*8*8
        self.samp_rate = samp_rate = 6e6
        self.wnT = wnT = math.pi/4.0*0+0.635
        self.vga_gain = vga_gain = 15
        self.pulse_freq = pulse_freq = 146e6
        self.mixer_gain = mixer_gain = 10
        self.lna_gain = lna_gain = 1
        self.freq_shift = freq_shift = 0.0
        self.final_samp_rate = final_samp_rate = samp_rate/total_decimation

        ##################################################
        # Blocks
        ##################################################
        self._wnT_range = Range(0.001, math.pi, 0.001, math.pi/4.0*0+0.635, 200)
        self._wnT_win = RangeWidget(self._wnT_range, self.set_wnT, "PLL Loop BW", "counter_slider", float)
        self.top_grid_layout.addWidget(self._wnT_win, 8,0,1,1)
        self._vga_gain_range = Range(0, 15, 1, 15, 200)
        self._vga_gain_win = RangeWidget(self._vga_gain_range, self.set_vga_gain, "VGA Gain", "counter_slider", int)
        self.top_grid_layout.addWidget(self._vga_gain_win, 0,0,1,1)
        self._mixer_gain_range = Range(0, 15, 1, 10, 200)
        self._mixer_gain_win = RangeWidget(self._mixer_gain_range, self.set_mixer_gain, "Mixer Gain", "counter_slider", int)
        self.top_grid_layout.addWidget(self._mixer_gain_win, 1,0,1,1)
        self._lna_gain_range = Range(0, 14, 1, 1, 200)
        self._lna_gain_win = RangeWidget(self._lna_gain_range, self.set_lna_gain, "LNA Gain", "counter_slider", int)
        self.top_grid_layout.addWidget(self._lna_gain_win, 2,0,1,1)
        self._freq_shift_range = Range(-500e3, 500e3, 1e3, 0.0, 200)
        self._freq_shift_win = RangeWidget(self._freq_shift_range, self.set_freq_shift, "Frequency Shift", "counter_slider", float)
        self.top_grid_layout.addWidget(self._freq_shift_win, 3,0,1,1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
        	int(final_samp_rate*10.0), #size
        	final_samp_rate, #samp_rate
        	"Pulse Processing Views", #name
        	1 #number of inputs
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
        
        labels = ["Pulse", "Im{Filtered}", "Re{Downconverted}", "Im{Downconverted}", "|Correlation|",
                  "zero", "Re{Ref Out}", "Im{Ref Out}", "Ref Frequency", "zero"]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "magenta",
                  "cyan", "dark green", "dark red", "Dark Blue", "Dark Blue"]
        styles = [1, 3, 2, 2, 1,
                  0, 1, 1, 3, 0]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        
        for i in xrange(1):
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
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 9,0,1,1)
        self.qtgui_number_sink_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_VERT,
            1
        )
        self.qtgui_number_sink_0.set_update_time(0.005)
        self.qtgui_number_sink_0.set_title("Pulse Indicator")
        
        labels = ["Raw", "Raw RO PLL", "", "", "",
                  "", "", "", "", ""]
        units = ["", "", "", "", "",
                 "", "", "", "", ""]
        colors = [("blue", "red"), ("blue", "red"), ("black", "black"), ("black", "black"), ("black", "black"),
                  ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        for i in xrange(1):
            self.qtgui_number_sink_0.set_min(i, 0)
            self.qtgui_number_sink_0.set_max(i, 1)
            self.qtgui_number_sink_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0.set_label(i, labels[i])
            self.qtgui_number_sink_0.set_unit(i, units[i])
            self.qtgui_number_sink_0.set_factor(i, factor[i])
        
        self.qtgui_number_sink_0.enable_autoscale(False)
        self._qtgui_number_sink_0_win = sip.wrapinstance(self.qtgui_number_sink_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_win, 9,1,1,1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
        	8192, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	pulse_freq, #fc
        	final_samp_rate, #bw
        	"Spectrum", #name
        	1 #number of inputs
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.01)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, -40)
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, -65.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        
        if not True:
          self.qtgui_freq_sink_x_0.disable_legend()
        
        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_freq_sink_x_0.set_plot_pos_half(not True)
        
        labels = ["Spectrum", "", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 7,0,1,1)
        self.PulseDetectBase = PulseDetectBase(
            freq_shift=freq_shift,
            lna_gain=lna_gain,
            mixer_gain=mixer_gain,
            pulse_freq=pulse_freq,
            vga_gain=vga_gain,
            wnT=wnT,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.PulseDetectBase, 1), (self.qtgui_freq_sink_x_0, 0))    
        self.connect((self.PulseDetectBase, 0), (self.qtgui_number_sink_0, 0))    
        self.connect((self.PulseDetectBase, 0), (self.qtgui_time_sink_x_0, 0))    

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "PulseDetectGUI")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


    def get_total_decimation(self):
        return self.total_decimation

    def set_total_decimation(self, total_decimation):
        self.total_decimation = total_decimation
        self.set_final_samp_rate(self.samp_rate/self.total_decimation)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_final_samp_rate(self.samp_rate/self.total_decimation)

    def get_wnT(self):
        return self.wnT

    def set_wnT(self, wnT):
        self.wnT = wnT
        self.PulseDetectBase.set_wnT(self.wnT)

    def get_vga_gain(self):
        return self.vga_gain

    def set_vga_gain(self, vga_gain):
        self.vga_gain = vga_gain
        self.PulseDetectBase.set_vga_gain(self.vga_gain)

    def get_pulse_freq(self):
        return self.pulse_freq

    def set_pulse_freq(self, pulse_freq):
        self.pulse_freq = pulse_freq
        self.PulseDetectBase.set_pulse_freq(self.pulse_freq)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.pulse_freq, self.final_samp_rate)

    def get_mixer_gain(self):
        return self.mixer_gain

    def set_mixer_gain(self, mixer_gain):
        self.mixer_gain = mixer_gain
        self.PulseDetectBase.set_mixer_gain(self.mixer_gain)

    def get_lna_gain(self):
        return self.lna_gain

    def set_lna_gain(self, lna_gain):
        self.lna_gain = lna_gain
        self.PulseDetectBase.set_lna_gain(self.lna_gain)

    def get_freq_shift(self):
        return self.freq_shift

    def set_freq_shift(self, freq_shift):
        self.freq_shift = freq_shift
        self.PulseDetectBase.set_freq_shift(self.freq_shift)

    def get_final_samp_rate(self):
        return self.final_samp_rate

    def set_final_samp_rate(self, final_samp_rate):
        self.final_samp_rate = final_samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(self.pulse_freq, self.final_samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.final_samp_rate)


def main(top_block_cls=PulseDetectGUI, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
