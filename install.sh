#!/bin/bash

# Install Ansible
echo "Installing Ansible..."
sudo apt -qq update
sudo apt install -yq software-properties-common
sudo apt-add-repository -y ppa:ansible/ansible > /dev/null 2>&1
sudo apt install -yq ansible
sudo apt autoremove

# Install RemoteDAQ Server
echo "Configuring RemoteDAQ Server..."
sudo ansible-playbook remotedaq_server_setup.yml