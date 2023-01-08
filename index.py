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
    result = subprocess.run(["route", "-n"], capture_output=True).stdout.decode().split("\n")
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
    
    