#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Pulsedetectcmdlineudp
# Generated: Tue Nov 13 20:10:31 2018
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PulseDetectBase import PulseDetectBase  # grc-generated hier_block
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import VHFPulseDetect
import VHFPulseSender
import cmath
import math
import signal

class PulseDetectCmdLineUDP(gr.top_block):

    def __init__(self, pulse_freq=146e6, samp_rate=3e6, vga_gain=15):
        gr.top_block.__init__(self, "Pulsedetectcmdlineudp")

        ##################################################
        # Parameters
        ##################################################
        self.pulse_freq = pulse_freq
        self.samp_rate = samp_rate
        self.vga_gain = vga_gain

        ##################################################
        # Variables
        ##################################################
        self.total_decimation = total_decimation = 4*8*8
        self.final_samp_rate = final_samp_rate = samp_rate/total_decimation

        ##################################################
        # Blocks
        ##################################################
        self.blocks_vector_sink_PulseDetectBase_raw = blocks.vector_sink_c(1)
        self.VHFPulseDetect_pulse_detect_sink_0 = blocks.vector_sink_f(1)
        self.VHFPulseDetect_pulse_detect_sink_1 = blocks.vector_sink_f(1)
        self.VHFPulseDetect_pulse_detect_sink_2 = blocks.vector_sink_f(1)
        self.VHFPulseDetect_pulse_detect_sink_3 = blocks.vector_sink_f(1)
        self.VHFPulseDetect_pulse_detect_sink_4 = blocks.vector_sink_f(1)
        self.VHFPulseSender_udp_sender_f_0 = VHFPulseSender.udp_sender_f()
        self.VHFPulseDetect_pulse_detect__ff_0 = VHFPulseDetect.pulse_detect__ff()
        self.PulseDetectBase = PulseDetectBase(
            freq_shift=0,
            lna_gain=11,
            mixer_gain=11,
            pulse_freq=pulse_freq,
            vga_gain=vga_gain,
            wnT=math.pi/4.0*0+0.635,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.PulseDetectBase, 0), (self.VHFPulseDetect_pulse_detect__ff_0, 0))    
        self.connect((self.PulseDetectBase, 1), (self.blocks_vector_sink_PulseDetectBase_raw, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 0), (self.VHFPulseSender_udp_sender_f_0, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 1), (self.VHFPulseDetect_pulse_detect_sink_0, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 2), (self.VHFPulseDetect_pulse_detect_sink_1, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 3), (self.VHFPulseDetect_pulse_detect_sink_2, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 4), (self.VHFPulseDetect_pulse_detect_sink_3, 0))    
        self.connect((self.VHFPulseDetect_pulse_detect__ff_0, 5), (self.VHFPulseDetect_pulse_detect_sink_4, 0))    

        # The following line is modified from the .grc output. It connects the two objects
        # such that udp_sender can change parameters in PulseDetectBase.
        self.VHFPulseSender_udp_sender_f_0.setPulseDetectBase(self.PulseDetectBase)

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

    def get_total_decimation(self):
        return self.total_decimation

    def set_total_decimation(self, total_decimation):
        self.total_decimation = total_decimation
        self.set_final_samp_rate(self.samp_rate/self.total_decimation)

    def get_final_samp_rate(self):
        return self.final_samp_rate

    def set_final_samp_rate(self, final_samp_rate):
        self.final_samp_rate = final_samp_rate


def argument_parser():
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option(
        "", "--pulse-freq", dest="pulse_freq", type="eng_float", default=eng_notation.num_to_str(146e6),
        help="Set pulse_freq [default=%default]")
    parser.add_option(
        "", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(3e6),
        help="Set samp_rate [default=%default]")
    parser.add_option(
        "", "--vga-gain", dest="vga_gain", type="int", default=15,
        help="Set vga_gain [default=%default]")
    return parser


def main(top_block_cls=PulseDetectCmdLineUDP, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    tb = top_block_cls(pulse_freq=options.pulse_freq, samp_rate=options.samp_rate, vga_gain=options.vga_gain)
    tb.start()
    #try:
    #    raw_input('Press Enter to quit: ')
    #except EOFError:
    #    pass
    while True:
        signal.pause()

    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
