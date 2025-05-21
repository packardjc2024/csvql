#!/bin/bash

# Load the .env file
source .env

# Move into the project's root directory
cd ~/${PROJECT_NAME}

# Decrypte GitHub Token
SECOND_KEY=$(echo $SECOND_KEY | openssl enc -aes-256-cbc -d -base64 -pbkdf2 -pass pass:${FIRST_KEY} -A)
GH_TOKEN=$(echo $GH_TOKEN | openssl enc -aes-256-cbc -d -base64 -pbkdf2 -pass pass:${SECOND_KEY} -A)

# Pull the GitHub repository
git stash
git pull https://${GH_USER}:${GH_TOKEN}@github.com/${GH_USER}/${PROJECT_NAME}
git stash clear

# Make sure permissions are still good for new update file
sudo chmod u+x update.sh

# Copy root files in case of updates
cp .env db/.env
cp .env web/.env
cp .dockerignore db/.dockerignore
cp .dockerignore web/.dockerignore

# Rebuild the containers
docker compose up --build -d

# Make sure volumes permissions are correct
sudo groupadd staticgroup
sudo usermod -aG staticgroup www-data

PATH_DIRECTORIES=(
    '/var' '/var/lib' 
    '/var/lib/docker' 
    '/var/lib/docker/volumes'
)
VOLUME_DIRECTORIES=(
    "/var/lib/docker/volumes/${PROJECT_NAME}_static_volume" 
    "/var/lib/docker/volumes/${PROJECT_NAME}_media_volume" 
    "/var/lib/docker/volumes/${PROJECT_NAME}_logs_volume" 
)

for path_directory in ${PATH_DIRECTORIES[@]}; do
    sudo chown :staticgroup $path_directory
    sudo chmod g+x $path_directory
done

for volume_directory in ${VOLUME_DIRECTORIES[@]}; do
    sudo chown -R :staticgroup $volume_directory
    sudo chmod -R g+xwr $volume_directory
done

exit
