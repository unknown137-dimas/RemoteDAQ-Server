#!/bin/bash

#Check Shell Argument
if [[ $# -eq 0 ]]
then
    echo 'No Zerotier ID supplied'
    exit 1
else

    #Join Zerotier Network
    sudo zerotier-cli join $1
    export ZT_ID=$(sudo zerotier-cli info | cut -d ' ' -f 3)
    
    #Deploy
    docker volume create --name=influxdb-data
    docker-compose up -d
fi
