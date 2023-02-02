#!/usr/bin/python

import sys

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange, custom, quietRun, dumpNetConnections
from mininet.cli import CLI

from time import sleep, time
from subprocess import Popen, PIPE
import subprocess
import argparse
import os

parser = argparse.ArgumentParser(description="Mininet pyswitch topology")
# no arguments needed as yet :-)
args = parser.parse_args()
lg.setLogLevel('info')

'''
nodes = {
    "server1": {
        "mac": "10:00:00:00:00:{:02x}",
        "ip": "192.168.100.1/24"
    },
    "server2": {
        "mac": "20:00:00:00:00:{:02x}",
        "ip": "192.168.100.2/24"
    },
    "client": {
        "mac": "30:00:00:00:00:{:02x}",
        "ip": "192.168.100.3/24"
    },
    "hub": {
        "mac": "40:00:00:00:00:{:02x}",
    }
}
'''


class PySwitchTopo(Topo):

    def __init__(self, args):
        # Add default members to class.
        super(PySwitchTopo, self).__init__()

        # Host and link configuration
        #
        #
        #   server1 
        #          \       / clinent1
        #   server2 ---hub
        #          /       \client 2
        #   server3 
        #

        nodeconfig = {"cpu": -1}
        '''
        for node in nodes.keys():
            self.addHost(node, **nodeconfig)
        for node in nodes.keys():
            # all links are 10Mb/s, 100 millisecond prop delay
            if node != "hub":
                self.addLink(node, "hub", bw=10, delay="100ms")
        '''
        self.addHost('server1',**nodeconfig)
        self.addHost('server2',**nodeconfig)
        self.addHost('server3',**nodeconfig)
        self.addHost('hub',**nodeconfig)
        self.addHost('client1',**nodeconfig)
        self.addHost('client2',**nodeconfig)

        for node in ['server1','server2','server3','client1','client2']:
            self.addLink(node,'hub',bw=10,delay='10ms')

def set_ip(net, node1, node2, ip):
    node1 = net.get(node1)
    ilist = node1.connectionsTo(net.get(node2))  # returns list of tuples
    intf = ilist[0]
    intf[0].setIP(ip)


def reset_macs(net, node, macbase):
    ifnum = 1
    node_object = net.get(node)
    for intf in node_object.intfList():
        node_object.setMAC(macbase.format(ifnum), intf)
        ifnum += 1

    for intf in node_object.intfList():
        print(node, intf, node_object.MAC(intf))


def set_route(net, fromnode, prefix, nextnode):
    node_object = net.get(fromnode)
    ilist = node_object.connectionsTo(net.get(nextnode))
    node_object.setDefaultRoute(ilist[0][0])


def setup_addressing(net):
    '''
    for node, config in nodes.items():
        reset_macs(net, node, config["mac"])
        if node != "hub":
            set_ip(net, node, "hub", config["ip"])
    '''
    reset_macs(net,'server1','10:00:00:00:00:{:02x}')
    reset_macs(net,'server2','20:00:00:00:00:{:02x}')
    reset_macs(net,'server3','30:00:00:00:00:{:02x}')
    reset_macs(net,'hub','60:00:00:00:00:{:02x}')
    reset_macs(net,'client1','40:00:00:00:00:{:02x}')
    reset_macs(net,'client2','50:00:00:00:00:{:02x}')
    set_ip(net,'server1','hub','192.168.100.1/24')
    set_ip(net,'server2','hub','192.168.100.2/24')
    set_ip(net,'server3','hub','192.168.100.3/24')
    set_ip(net,'client1','hub','192.168.100.4/24')
    set_ip(net,'client2','hub','192.168.100.5/24')



def disable_ipv6(net):
    for v in net.values():
        v.cmdPrint('sysctl -w net.ipv6.conf.all.disable_ipv6=1')
        v.cmdPrint('sysctl -w net.ipv6.conf.default.disable_ipv6=1')


def main():
    topo = PySwitchTopo(args)
    net = Mininet(controller=None, topo=topo, link=TCLink, cleanup=True)
    setup_addressing(net)
    disable_ipv6(net)
    net.interact()


if __name__ == '__main__':
    main()
