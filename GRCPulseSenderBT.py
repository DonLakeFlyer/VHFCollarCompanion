"""
Embedded Python Blocks:

Each this file is saved, GRC will instantiate the first class it finds to get
ports and parameters of your block. The arguments to __init__  will be the
parameters. All of them are required to have default values!
"""
import numpy as np
import bluetooth
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self, factor=1.0):  # only default arguments here
        gr.sync_block.__init__(
            self,
            name='Embedded Python Block',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
        self.factor = factor
        self.serverSocket = None


    def work(self, input_items, output_items):
        if not self.serverSocket:
                # Setup bluetooth socket
                self.serverSocket = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
                self.serverSocket.bind(("", 0x1001))
                self.serverSocket.listen(1)

                # Advertise service
                uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
                bluetooth.advertise_service(
				self.serverSocket,
				"PulseServer",
				service_id = uuid,
				service_classes = [ uuid, SERIAL_PORT_CLASS ],
				profiles = [ SERIAL_PORT_PROFILE ])
                #logging.debug("Waiting for bluetooth connection")
                #self.clientSocket, clientInfo = self.serverSocket.accept()
                #print("Accepted connection from ", clientInfo)
                #self.clientSocket.setblocking(False)

        print "length of input vector =",  len(input_items[0])
        print "length of output vector =",  len(output_items[0])
        output_items[0][:] = input_items[0]
        return len(output_items[0])
