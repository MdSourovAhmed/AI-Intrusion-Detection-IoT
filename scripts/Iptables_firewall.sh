#!/bin/bash

# Flush old rules
iptables -F
iptables -X

# Allow loopback and established connections
sudo iptables -A INPUT -p tcp --dport 1883 -m connlimit --connlimit-above 10 --connlimit-mask 32 -j LOG --log-prefix "MQTT CONN LIMIT: "
