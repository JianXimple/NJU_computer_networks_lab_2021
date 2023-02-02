'''
Ethernet learning switch in Python.

Note that this file currently has the code to implement a "hub"
in it, not a learning switch.  (I.e., it's currently a switch
that doesn't learn.)
'''
import switchyard
from switchyard.lib.userlib import *

Max_num = 5 #max number of rules
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

        log_debug (f"In {net.name} received packet {packet} on {fromIface}")
        eth = packet.get_header(Ethernet)
        for md in table:
            table[md][1]+=1
        if eth.src in table:
            table[eth.src][0]=fromIface
        elif len(table)<Max_num:
            table[eth.src]=[fromIface,0]
        else:
            lru_key=list(table.keys())[0]
            for key in table:
                if table[key][1]>table[lru_key][1]:
                    lru_key=key
            del table[lru_key]
            table[eth.src]=[fromIface,0]

        if eth is None:
            log_info("Received a non-Ethernet packet?!")
            return
        if eth.dst in mymacs:
            log_info("Received a packet intended for me")
        elif eth.dst in table:
            out_port = table[eth.dst][0]
            table[eth.dst][1]=0
            log_debug("Forward packet {} to {}".format(packet,out_port))
            net.send_packet(out_port,packet)
        else:
            for intf in my_interfaces:
                if fromIface!= intf.name:
                    log_info (f"Flooding packet {packet} to {intf.name}")
                    net.send_packet(intf, packet)

    net.shutdown()
