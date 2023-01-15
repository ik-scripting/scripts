#!/bin/bash

# Install the necessary packages
apt update
apt install -y ufw

# Allow SSH connections
ufw allow ssh

# Enable the firewall
ufw enable
