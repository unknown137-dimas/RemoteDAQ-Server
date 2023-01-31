#!/bin/bash

#User Input
read -p 'Input ZeroTier network ID: ' ztid
read -p 'Input DB username: ' dbuser
read -sp 'Input DB password: ' dbpass
read -p 'Input DB org name: ' dborg
read -p 'Input DB bucket name: ' dbbucket

#Update Helper Scripts Permission
chmod +x scripts/*

#Run Helper Scripts
./scripts/install.sh
./scripts/deploy.sh $ztid $dbuser $dbpass $dborg $dbbucket