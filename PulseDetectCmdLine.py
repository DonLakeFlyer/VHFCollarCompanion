#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Pulsedetectcmdline
# Generated: Wed Aug  1 13:17:00 2018
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from GRCEmbeddedPulseDetect import blk
from PulseDetectBase import PulseDetectBase  # grc-generated hier_block
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import cmath
import math


class PulseDetectCmdLine(gr.top_block):

    def __init__(self, pulse_freq=146e6, samp_rate=3e6):
        gr.top_block.__init__(self, "Pulsedetectcmdline")

        ##################################################
        # Parameters
        ##################################################
        self.pulse_freq = pulse_freq
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.total_decimation = total_decimation = 4*8*8
        self.final_samp_rate = final_samp_rate = samp_rate/total_decimation

        ##################################################
        # Blocks
        ##################################################
        self.blocks_vector_sink_x_1 = blocks.vector_sink_f(1)
        self.blocks_vector_sink_x_0 = blocks.vector_sink_c(1)
        self.PulseDetectBase = PulseDetectBase(
            freq_shift=0,
            lna_gain=1,
            mixer_gain=10,
            pulse_freq=pulse_freq,
            vga_gain=15,
            wnT=math.pi/4.0*0+0.635,
        )
        self.GRCEmbeddedPulseDetect = blk(sample_rate=samp_rate)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.GRCEmbeddedPulseDetect, 0), (self.blocks_vector_sink_x_1, 0))    
        self.connect((self.PulseDetectBase, 0), (self.GRCEmbeddedPulseDetect, 0))    
        self.connect((self.PulseDetectBase, 1), (self.blocks_vector_sink_x_0, 0))    

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
    return parser


def main(top_block_cls=PulseDetectCmdLine, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    tb = top_block_cls(pulse_freq=options.pulse_freq, samp_rate=options.samp_rate)
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
