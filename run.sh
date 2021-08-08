#!/bin/sh

if ! command -v docker-compose &> /dev/null
then
    echo "Please make sure you have docker and docker-compose installed in your system before running this script."
    exit
fi

docker-compose down
TEXT_FILENAME=$1 docker-compose up
