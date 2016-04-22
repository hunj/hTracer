#!/usr/bin/python

"""
hTracer: a hop/RTT measurement tool
Hun Jae Lee (hxl224)
EECS325 Computer Networks Project 2
"""

import socket
import struct
import time
import ctypes

## Environment setup
PORT = 33444    # most implementations of traceroute use ports from 33434 to 33534.
MAX_HOPS = 32   # initial TTL value specified in the assignment

# ICMP socket is for sending back ICMP packets and requires a raw socket (SOCK_RAW)
ICMP = socket.getprotobyname('icmp')
# UDP socket is for probing and requires datagram socket (SOCK_DGRAM)
UDP = socket.getprotobyname('udp')

VERBOSE = True

## End environment setup

def main(target_file):
    """
    main function contains the flow of the logic.
    returns a List that contains tuples of (target, ttl, rtt)
    """
    result = []
    for target in find_targets_in_file(target_file):
        ttl, rtt = number_of_hops_and_RTT_to(target)
        result.append( (target, ttl, rtt) )
    print("<SYSTEM>: Probing complete. Result:")
    print result
    

def create_sockets(ttl):
    """
    creates sockets (both sending and receiving) and returns them
    """
    # Socket instances 
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, UDP)
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP)

    # Set socket options
    send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    timeout = struct.pack("ll", 5, 0)
    recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

    return recv_socket, send_socket

def find_targets_in_file(filename):
    """
    Loads the specified file of IP address lists, 
    read line-by-line and add to the targets list.
    """
    with open(filename) as target_file:
        targets = target_file.read().splitlines()
    return targets

def calculate_distance_between(host1, host2):
    return 1

def number_of_hops_and_RTT_to(destination_name):
    # destination address and port
    print "<SYSTEM>: Probing '%s'..." % destination_name
    destination_address = socket.gethostbyname(destination_name)

    # TTL is the number of "hops"
    ttl = 1
    rtt = 0

    while 1:
        recv_socket, send_socket = create_sockets(ttl)
        current_time = time.time()

        # specify the port and an empty string for the hostname
        recv_socket.bind(("", PORT))

        # send to the destination host (on the same port)
        send_socket.sendto("", (destination_name, PORT))

        # placeholders
        current_address = None
        current_name = None

        try:
            # socket.recvfrom gives back (data, address) but we only need the address part
            packet, current_address = recv_socket.recvfrom(512)
            current_address = current_address[0]

            payload = len(packet[56:])
            ip_header = struct.unpack('!BBHHHBBH4s4s', packet[0:20])
            # print(ip_header)

            # The resolution can fail and result in an exception, 
            # in which case we'll want to catch it and make the hostname the same as the address
            try:
                # reverse DNS resolution lookup
                current_name = socket.gethostbyaddr(current_address)[0]
            except socket.error:
                current_name = current_address
        except socket.error, (value, message):
            print "< ERROR >: Something went wrong: " + message
            pass
        finally:
            send_socket.close()
            recv_socket.close()

        # Print 
        if VERBOSE:
            if current_address is not None:
                current_host = "%s : %s" % (current_address, current_name)
            else:
                current_host = "*"
            print "%d\t%s" % (ttl, current_host)        

        # Ending condition:
        # Either we have reached our destination, 
        # or we have exceeded some maximum number of hops
        if current_address == destination_address or ttl > MAX_HOPS:
            rtt = time.time() - current_time
            print("<SYSTEM>: Probing '%s' complete. TTL: %s, RTT: %d" % (destination_name, ttl, rtt*1000))
            return ttl, rtt * 1000 # rtt is calculated in seconds, we want milliseconds

        ttl += 1

# This runs the code.
if __name__ == "__main__":
    print main("targets.txt")