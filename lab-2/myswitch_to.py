'''
Ethernet learning switch in Python.

Note that this file currently has the code to implement a "hub"
in it, not a learning switch.  (I.e., it's currently a switch
that doesn't learn.)
'''
import switchyard
from switchyard.lib.userlib import *
import time

def main(net: switchyard.llnetbase.LLNetBase):
    my_interfaces = net.interfaces()
    mymacs = [intf.ethaddr for intf in my_interfaces]
    table={}
    while True:
        try:
            _, fromIface, packet = net.recv_packet()
        except NoPackets:
            continue
        except Shutdown:
            break
        
        t=time.time()
        eth = packet.get_header(Ethernet)
        table[eth.src]=[fromIface,t]
        for mac in list(table.keys()):
            if ((t-table[mac][1])>10):
                del table[mac]
        log_debug (f"In {net.name} received packet {packet} on {fromIface}")

        if eth is None:
            log_info("Received a non-Ethernet packet?!")
            return
        if eth.dst in mymacs:
            log_info("Received a packet intended for me")
        elif eth.dst in table:
            output_port=table[eth.dst][0]
            log_debug("Forward packet {} to {}".format(packet,output_port))
            net.send_packet(output_port,packet)
        else:
            for intf in my_interfaces:
                if fromIface!= intf.name:
                    log_info (f"Flooding packet {packet} to {intf.name}")
                    net.send_packet(intf, packet)

    net.shutdown()
