#!/bin/bash

#User Input
read -p 'Input ZeroTier network ID: ' zt_net_id
read -p 'Input ZeroTier Token: ' zt_token
read -p 'Input DB username: ' dbuser
read -sp 'Input DB password: ' dbpass
read -p 'Input DB org name: ' dborg
read -p 'Input DB bucket name: ' dbbucket

#Update Helper Scripts Permission
chmod +x scripts/*

#Run Helper Scripts
./scripts/install.sh
./scripts/deploy.sh $zt_net_id $zt_token $dbuser $dbpass $dborg $dbbucket