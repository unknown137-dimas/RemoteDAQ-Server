#!/bin/bash

# Install Ansible
echo "Installing Ansible..."
sudo apt update > /dev/null 2>&1
sudo apt install -y software-properties-common > /dev/null 2>&1
sudo apt-add-repository -y ppa:ansible/ansible > /dev/null 2>&1
sudo apt install -y ansible-core ansible > /dev/null 2>&1
sudo apt -y autoremove > /dev/null 2>&1

# Setup RemoteDAQ Server
echo "Configuring RemoteDAQ Server..."
sudo ansible-playbook remotedaq_server_setup.yml