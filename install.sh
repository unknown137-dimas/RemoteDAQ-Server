#!/bin/bash

# Install Ansible
sudo apt update
sudo apt install software-properties-common
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt install ansible

# Install RemoteDAQ Server
sudo ansible-playbook remotedaq_server_setup.yml