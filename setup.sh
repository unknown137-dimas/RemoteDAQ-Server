#!/bin/bash

#Zerotier Config
sudo zerotier-cli join $1
export ZT_ID=$(sudo zerotier-cli info | cut -d ' ' -f 3)

#Deploy
docker-compose up -d