#!/usr/bin/python

import socket
import struct
import time
import ctypes
import math
import requests

## Environment setup
PORT = 33444    # most implementations of traceroute use ports from 33434 to 33534.
MAX_HOPS = 32   # initial TTL value specified in the assignment

# ICMP socket is for sending back ICMP packets and requires a raw socket (SOCK_RAW)
ICMP = socket.getprotobyname('icmp')
# UDP socket is for probing and requires datagram socket (SOCK_DGRAM)
UDP = socket.getprotobyname('udp')

# whether if you want to use the verbose mode
VERBOSE = True
## End environment setup

def main(target_file, result_file):
    """
    main function contains the flow of the logic.
    returns a tuple of (target, ttl, rtt).
    """
    # prepare data storage for result
    raw_result = []
    result = open(result_file, 'w')

    source_ip = requests.get('http://ifconfig.co/json').json()["ip"]

    # make it pretty
    result.write("host,TTL,RTT,Dist\n")

    # run on each target
    for target in find_targets_in_file(target_file):
        ttl, rtt = number_of_hops_and_RTT_to(target)
        dist = calculate_distance_between(source_ip, target)
        raw_result.append( (target, ttl, rtt, dist) )
        result.write("%s,%s,%s,%s\n" % (target, ttl, rtt, dist))
    print("<SYSTEM>: Probing complete. Result:")
    print(raw_result)
    result.close()
    # good bye

def create_sockets(ttl):
    """
    creates sockets (both sending and receiving) and returns them
    """
    # Socket instances 
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, UDP)
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW,  ICMP)

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
    """
    finds geolocations of the given two tuples of (latitude, longitude) and 
    calculate their distance.

    Source: https://gist.github.com/rochacbruno/2883505
    """

    lat1, lon1 = coordinates_of(host1)
    lat2, lon2 = coordinates_of(host2)
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def coordinates_of(ip_address):
    """
    finds the coordinates of given IP address.
    """
    json_request = requests.get('http://freegeoip.net/json/%s' % ip_address).json()
    return json_request['latitude'], json_request['longitude']

def number_of_hops_and_RTT_to(destination_name):
    """
    Finds the number of hops and the RTT to given destination.
    """
    # destination address and port
    print("<SYSTEM>: Probing '%s'..." % destination_name)
    destination_address = socket.gethostbyname(destination_name)

    # TTL is the number of "hops"
    ttl = 1
    rtt = time.time()

    while 1:
        recv_socket, send_socket = create_sockets(ttl)
        
        # specify the port and an empty string for the hostname
        recv_socket.bind(("", PORT))

        # send to the destination host (on the same port)
        send_socket.sendto(b'', (destination_name, PORT))

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
        except socket.error (value, message):
            if message != "Resource temporarily unavailable":
                print("< ERROR >: Something went wrong: " + message)
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
            print("%d\t%s" % (ttl, current_host))

        # Ending condition:
        # Either we have reached our destination, 
        # or we have exceeded some maximum number of hops
        if current_address == destination_address or ttl >= MAX_HOPS:
            rtt = time.time() - rtt
            source_ip = requests.get('http://ifconfig.co/json').json()["ip"]
            print("<SYSTEM>: Probing '%s' complete. TTL: %s, RTT: %fms, Distance: %fkm" % (destination_name, ttl, rtt*1000, calculate_distance_between(source_ip, destination_address)))

            return ttl, rtt * 1000 # rtt is calculated in seconds, we want milliseconds

        ttl += 1

# This runs the code.
if __name__ == "__main__":
    main("targets.txt", "result.csv")

