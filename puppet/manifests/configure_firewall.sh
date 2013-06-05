#!/bin/bash
#
# iptables configuration script
#
# Flush all current rules from iptables
#
 iptables -F
#
# Set default policies for INPUT, FORWARD and OUTPUT chains
#
 iptables -P INPUT DROP
 iptables -P FORWARD DROP
 iptables -P OUTPUT ACCEPT
#
# Accept packets belonging to established and related connections
#
 iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
#
# Set access for Internet Control Message Protocol (ICMP)
#
 iptables -A INPUT -p icmp -j ACCEPT
#
# Set access for localhost
#
 iptables -A INPUT -i lo -j ACCEPT
#
# Allow SSH connections on tcp port 22
# This is essential when working on remote servers via SSH to prevent locking yourself out of the system
#
 iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
#
# Allow Pyramid dev connections on tcp port 8080
#
 iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 8080 -j ACCEPT
#
# Allow PostgreSQL dev connections on tcp port 5432
#
 iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 5432 -j ACCEPT

#
# Reject all other input/forward packets
#
 iptables -A INPUT -j REJECT --reject-with icmp-host-prohibited
 iptables -A FORWARD -j REJECT --reject-with icmp-host-prohibited
#
# Save settings
#
 /sbin/service iptables save
#
# List rules
#
 iptables -S
