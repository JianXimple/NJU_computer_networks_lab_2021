#!/usr/bin/env python3

from switchyard.lib.userlib import *

def mk_pkt(hwsrc, hwdst, ipsrc, ipdst, reply=False):
    ether = Ethernet(src=hwsrc, dst=hwdst, ethertype=EtherType.IP)
    ippkt = IPv4(src=ipsrc, dst=ipdst, protocol=IPProtocol.ICMP, ttl=32)
    icmppkt = ICMP()
    if reply:
        icmppkt.icmptype = ICMPType.EchoReply
    else:
        icmppkt.icmptype = ICMPType.EchoRequest
    return ether + ippkt + icmppkt

def switch_tests():
    s = TestScenario("switch_to tests")
    s.add_interface('eth0', '10:00:00:00:00:01')
    s.add_interface('eth1', '10:00:00:00:00:02')
    s.add_interface('eth2', '10:00:00:00:00:03')

    # step 1: a frame with dst address not in table
    # the packet will be flooded out
    # repeat this step until the table is full 
    reqpkt = mk_pkt("30:00:00:00:00:01", "40:00:00:00:00:01", '192.168.1.100','172.16.42.3')
    s.expect(PacketInputEvent("eth0", reqpkt, display=Ethernet), "An Ethernet frame from 3:00:00:00:00:01 to 40:00:00:00:00:01 should arrive on eth0")
    s.expect(PacketOutputEvent("eth1", reqpkt, "eth2", reqpkt, display=Ethernet), "Ethernet frame destined for 40:00:00:00:00:01 should be flooded out eth1 and eth2")

    reqpkt = mk_pkt("30:00:00:00:00:02", "40:00:00:00:00:01", '192.168.2.100','172.16.42.3')
    s.expect(PacketInputEvent("eth0", reqpkt, display=Ethernet), "An Ethernet frame from 3:00:00:00:00:02 to 40:00:00:00:00:01 should arrive on eth0")
    s.expect(PacketOutputEvent("eth1", reqpkt, "eth2", reqpkt, display=Ethernet), "Ethernet frame destined for 40:00:00:00:00:01 should be flooded out eth1 and eth2")
    
    reqpkt = mk_pkt("30:00:00:00:00:03", "40:00:00:00:00:01", '192.168.3.100','172.16.42.3')
    s.expect(PacketInputEvent("eth1", reqpkt, display=Ethernet), "An Ethernet frame from 30:00:00:00:00:03 to 40:00:00:00:00:01 should arrive on eth1")
    s.expect(PacketOutputEvent("eth0", reqpkt, "eth2", reqpkt, display=Ethernet), "Ethernet frame destined for 40:00:00:00:00:01 should be flooded out eth0 and eth2")

    reqpkt = mk_pkt("30:00:00:00:00:04", "40:00:00:00:00:01", '192.168.4.100','172.16.42.3')
    s.expect(PacketInputEvent("eth1", reqpkt, display=Ethernet), "An Ethernet frame from 30:00:00:00:00:04 to 40:00:00:00:00:01 should arrive on eth1")
    s.expect(PacketOutputEvent("eth0", reqpkt, "eth2", reqpkt, display=Ethernet), "Ethernet frame destined for 40:00:00:00:00:01 should be flooded out eth0 and eth2")

    reqpkt = mk_pkt("30:00:00:00:00:05", "40:00:00:00:00:01", '192.168.5.100','172.16.42.3')
    s.expect(PacketInputEvent("eth2", reqpkt, display=Ethernet), "An Ethernet frame from 30:00:00:00:00:05 to 40:00:00:00:00:01 should arrive on eth1")
    s.expect(PacketOutputEvent("eth0", reqpkt, "eth1", reqpkt, display=Ethernet), "Ethernet frame destined for 40:00:00:00:00:01 should be flooded out eth0 and eth1")


    # step 2: now the table is full and 30:00:00:00:00:01 is associated with eth0
    # a frame with the dst address 30:00:00:00:00:01 will be forwarded out instead of flooding
    reqpkt = mk_pkt("30:00:00:00:00:03", "30:00:00:00:00:01", '192.168.3.100','192.168.1.100')
    s.expect(PacketInputEvent("eth1", reqpkt, display=Ethernet), "An Ethernet frame from 30:00:00:00:00:03 to 30:00:00:00:00:01 should arrive on eth1")
    s.expect(PacketOutputEvent("eth0", reqpkt, display=Ethernet), "Ethernet frame destined for 30:00:00:00:00:01 should be forwarded out eth0")
    s.expect(PacketInputTimeoutEvent(1.0), "The switch should not do anything after it sends packet out frome eth0")
    
    reqpkt = mk_pkt("30:00:00:00:00:03", "30:00:00:00:00:02", '192.168.3.100','192.168.2.100')
    s.expect(PacketInputEvent("eth1", reqpkt, display=Ethernet), "An Ethernet frame from 30:00:00:00:00:03 to 30:00:00:00:00:02 should arrive on eth1")
    s.expect(PacketOutputEvent("eth0", reqpkt, display=Ethernet), "Ethernet frame destined for 30:00:00:00:00:02 should be forwarded out eth0")
    s.expect(PacketInputTimeoutEvent(1.0), "The switch should not do anything after it sends packet out frome eth0")

    reqpkt = mk_pkt("30:00:00:00:00:01", "30:00:00:00:00:03", '192.168.1.100','192.168.3.100')
    s.expect(PacketInputEvent("eth0", reqpkt, display=Ethernet), "An Ethernet frame from 30:00:00:00:00:01 to 30:00:00:00:00:03 should arrive on eth0")
    s.expect(PacketOutputEvent("eth1", reqpkt, display=Ethernet), "Ethernet frame destined for 30:00:00:00:00:03 should be forwarded out eth1")
    s.expect(PacketInputTimeoutEvent(1.0), "The switch should not do anything after it sends packet out frome eth1")

    reqpkt = mk_pkt("30:00:00:00:00:01", "30:00:00:00:00:04", '192.168.1.100','192.168.4.100')
    s.expect(PacketInputEvent("eth0", reqpkt, display=Ethernet), "An Ethernet frame from 30:00:00:00:00:01 to 30:00:00:00:00:04 should arrive on eth0")
    s.expect(PacketOutputEvent("eth1", reqpkt, display=Ethernet), "Ethernet frame destined for 30:00:00:00:00:04 should be forwarded out eth1")
    s.expect(PacketInputTimeoutEvent(1.0), "The switch should not do anything after it sends packet out frome eth1")

    # step 3: table is full & the traffic volume of each item is 2 except 30:00:00:00:00:05 is 1
    reqpkt = mk_pkt("30:00:00:00:00:06", "30:00:00:00:00:05", '192.168.6.100','192.168.5.100')
    s.expect(PacketInputEvent("eth0", reqpkt, display=Ethernet), "An Ethernet frame from 30:00:00:00:00:06 to 30:00:00:00:00:05 should arrive on eth0")
    s.expect(PacketOutputEvent("eth1", reqpkt, "eth2", reqpkt, display=Ethernet), "Ethernet frame destined for 30:00:00:00:00:05 should be flooded out")
    
    return s

scenario = switch_tests()