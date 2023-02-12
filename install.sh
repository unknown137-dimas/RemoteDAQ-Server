#!/bin/bash

# Install Ansible
sudo apt -qq update
sudo apt install -yq software-properties-common
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt install -yq ansible

# Install RemoteDAQ Server
sudo ansible-playbook remotedaq_server_setup.yml