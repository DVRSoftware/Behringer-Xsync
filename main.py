from osc import oscClient
from time import sleep

#Exclude Parameters
EXCLUDE=("/bus/01/mix/on","/bus/02/mix/on","/bus/03/mix/on","/bus/04/mix/on","/bus/05/mix/on","/bus/06/mix/on","/bus/07/mix/on","/bus/08/mix/on","/bus/09/mix/on","/bus/10/mix/on","/bus/11/mix/on","/bus/12/mix/on","/bus/13/mix/on","/bus/14/mix/on","/bus/15/mix/on","/bus/16/mix/on","/main/st/mix/on","/main/m/mix/on")

#IP-Address
IP_A="192.168.178.22"
IP_B="192.168.5.3"

#UDP-Port
# 10024 -> XR12, XR16, XR18
# 10023 -> X32
PORT=10023

#Verbose
# 0 -> Verbose off
# 1 -> Verbose on (Show each Message transmitting / receiving)
VERBOSE=0


#Data Transfer Client A to Client B
def handler_a(addr,value):
    if(not (addr in EXCLUDE)):
        client_b.send(addr,value)

#Data Transfer Client B to Client A
def handler_b(addr,value):
    if(not (addr in EXCLUDE)):
        client_a.send(addr,value)

if(__name__=="__main__"):
    #OSC-Instance for Client A
    client_a=oscClient(address=IP_A, port=PORT, handlerfunc=handler_a, verbose=VERBOSE) 
    client_a.validate_connection()

    #OSC-Instance for Client B
    client_b=oscClient(address=IP_B, port=PORT, handlerfunc=handler_b, verbose=VERBOSE)
    client_b.validate_connection()

    #Wait for the program to close
    while True:
        sleep(10)
