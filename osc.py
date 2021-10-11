import time
import threading
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.osc_message_builder import OscMessageBuilder

class OSCClientServer(BlockingOSCUDPServer):
    def __init__(self, address, dispatcher):
        super().__init__(('', 0), dispatcher)
        self.ip_address = address

    def send_message(self, address, value):
        builder = OscMessageBuilder(address = address)
        if value is None:
            values = []
        elif isinstance(value, list):
            values = value
        else:
            values = [value]
        for val in values:
            builder.add_arg(val)
        msg = builder.build()
        self.socket.sendto(msg.dgram, self.ip_address)

class oscClient:
    _CONNECT_TIMEOUT = 0.5
    _WAIT_TIME = 0.02
    _REFRESH_TIMEOUT = 5

    info_response = []
    
    def __init__(self, address, port, handlerfunc=None, verbose=0):
        self.verbose=verbose
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.msg_handler)
        self.server = OSCClientServer((address, port), dispatcher)
        self.handlerfunc = handlerfunc
        worker = threading.Thread(target = self.run_server)
        worker.daemon = True
        worker.start()
        worker = threading.Thread(target = self.refresh_connection)
        worker.daemon = True
        worker.start()

    def validate_connection(self):
        self.send('/xinfo')
        time.sleep(self._CONNECT_TIMEOUT)
        if len(self.info_response) > 0:
            if(self.verbose):
                print('Successfully connected to %s with firmware %s at %s.' % (self.info_response[2], 
                    self.info_response[3], self.info_response[0]))
        else:
            print('Error: Failed to setup OSC connection to mixer ('+str(self.server.ip_address[0])+':'+str(self.server.ip_address[1])+'). Please check for correct ip address.')
            exit()
        
    def run_server(self):
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.shutdown()
            exit()
        
    def msg_handler(self, addr, *data):
            if(self.verbose):
                print('OSC IN ('+str(self.server.ip_address[0])+':'+str(self.server.ip_address[1])+'):',data,"from",addr)
            if addr == '/xinfo':
                self.info_response = data
            else:
                if(self.handlerfunc!=None):
                    self.handlerfunc(addr, data[0])
    
    def refresh_connection(self):
        # Tells mixer to send changes in state that have not been recieved from this OSC Client
        #   /xremote        - all parameter changes are broadcast to all active clients (Max 4)
        #   /xremotefnb     - No Feed Back. Parameter changes are only sent to the active clients which didn't initiate the change
        try:
            while True:
                self.server.send_message("/xremotenfb", None)
                time.sleep(self._REFRESH_TIMEOUT)
        except KeyboardInterrupt:
            exit()
            
    def send(self, address, param = None):
        if(self.verbose):
            print('OSC OUT ('+str(self.server.ip_address[0])+':'+str(self.server.ip_address[1])+'):',param,"to",address)
        self.server.send_message(address, param)