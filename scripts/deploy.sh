#!/bin/bash

#Join Zerotier Network
sudo zerotier-cli join $1

#Populate .env File
echo ZT_ID=$(sudo zerotier-cli info | cut -d ' ' -f 3) >> .env
echo DOCKER_INFLUXDB_INIT_USERNAME=$2 >> .env
echo DOCKER_INFLUXDB_INIT_PASSWORD=$3 >> .env
echo DOCKER_INFLUXDB_INIT_ORG=$4 >> .env
echo DOCKER_INFLUXDB_INIT_BUCKET=$5 >> .env

#Deploy
touch settings.json
sudo docker volume create --name=influxdb-data
sudo docker-compose up -d
