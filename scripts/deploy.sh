#!/bin/bash

#User Input
read -p 'Input ZeroTier network ID: ' ztid
read -p 'Input DB username: ' dbuser
read -sp 'Input DB password: ' dbpass
read -p 'Input DB Org Name: ' dborg
read -p 'Input DB bucket Name: ' dbbucket

#Join Zerotier Network
sudo zerotier-cli join $ztid

#Populate .env File
echo ZT_ID=$(sudo zerotier-cli info | cut -d ' ' -f 3) >> .env
echo DOCKER_INFLUXDB_INIT_USERNAME=$dbuser >> .env
echo DOCKER_INFLUXDB_INIT_PASSWORD=$dbpass >> .env
echo DOCKER_INFLUXDB_INIT_ORG=$dborg >> .env
echo DOCKER_INFLUXDB_INIT_BUCKET=$dbbucket >> .env

#Deploy
touch settings.json
sudo docker volume create --name=influxdb-data
sudo docker-compose up -d
