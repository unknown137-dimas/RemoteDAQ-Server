#!/bin/bash

#Check Shell Argument
if [[ $# -eq 0 ]]
then
    echo 'No Zerotier Network ID supplied'
    exit 1
else

    #Join Zerotier Network
    sudo zerotier-cli join $1
    echo ZT_ID=$(sudo zerotier-cli info | cut -d ' ' -f 3) > .env
    
    #Deploy
    touch settings.json
    sudo docker volume create --name=influxdb-data
    sudo docker-compose up -d
fi
