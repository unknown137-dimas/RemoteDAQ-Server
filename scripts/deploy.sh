#!/bin/bash

#Join Zerotier Network
sudo zerotier-cli join $1

#Populate .env File
echo ZT_ID=$(sudo zerotier-cli info | cut -d ' ' -f 3) >> .env
echo ZT_NET_ID=$1 >> .env
echo DOCKER_INFLUXDB_INIT_USERNAME=$3 >> .env
echo DOCKER_INFLUXDB_INIT_PASSWORD=$4 >> .env
echo DOCKER_INFLUXDB_INIT_ORG=$5 >> .env
echo DOCKER_INFLUXDB_INIT_BUCKET=$6 >> .env

#Deploy
touch settings.json
sudo docker secret create zt_token $2
sudo docker volume create --name=influxdb-data
sudo docker-compose up -d
