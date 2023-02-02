#!/usr/bin/env python3

'''
Basic IPv4 router (static routing) in Python.
'''

import time
import switchyard
from switchyard.lib.userlib import *


class Router(object):
    def __init__(self, net: switchyard.llnetbase.LLNetBase):
        self.net = net
        self.interfaces=net.interfaces()
        self.ip_list=[intf.ipaddr for intf in self.interfaces]
        self.mac_list=[intf.ethaddr for intf in self.interfaces]
        self.arp_table={}
        # other initialization stuff here

    def handle_packet(self, recv: switchyard.llnetbase.ReceivedPacket):
        timestamp, ifaceName, packet = recv
        # TODO: your logic here
        log_debug("Got a packet:{}".format(str(packet)))
        log_info("Got a packet:{}".format(str(packet)))
        arp=packet.get_header(Arp)
        if arp is None:
            log_info("Not an arp packet")
        else:
            log_info("operation kind {}".format(str(arp.operation)))
            self.arp_table[arp.senderprotoaddr]=arp.senderhwaddr
            if arp.operation==1:
                log_info("arp requests")
                index =-1
                for i in range(len(self.ip_list)):
                    if self.ip_list[i]==arp.targetprotoaddr:
                        index =i
                        break
                if index!= -1:
                    log_info("match packet")
                    answer=create_ip_arp_reply(self.mac_list[index],arp.senderhwaddr,self.ip_list[index],arp.senderprotoaddr)
                    self.net.send_packet(ifaceName,answer)
                    log_info("send arp reply:{}".format(str(answer)))
            elif arp.operation==2:
                log_info("receive an arp reply")
                self.arp_table[arp.targetprotoaddr]=arp.targethwaddr
            else:
                log_info("receive unknown arp")
        log_info("Table shown as follows:")
        for k,v in self.arp_table.items():
            print(k,"\t",v)

    def start(self):
        '''A running daemon of the router.
        Receive packets until the end of time.
        '''
        while True:
            try:
                recv = self.net.recv_packet(timeout=1.0)
            except NoPackets:
                continue
            except Shutdown:
                break

            self.handle_packet(recv)

        self.stop()

    def stop(self):
        self.net.shutdown()


def main(net):
    '''
    Main entry point for router.  Just create Router
    object and get it going.
    '''
    router = Router(net)
    router.start()
