#!/bin/bash

source .build-env
source .env

DOCKER_BASE_DIR=.
DOCKER_IMAGE_NAME=$BUILD_IMAGE_NAME

# Variabile per la versione dell'immagine
DOCKER_IMAGE_VERSION=${BUILD_IMAGE_VERSION}-${BUILD_IMAGE_PLATFORM}-${BUILD_IMAGE_DEVELOPMENT_PREFIX}

echo Effettuo run $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION


# Nome del container
CONTAINER_NAME="fvgvision-dev"

# Immagine Docker da utilizzare
IMAGE_NAME="docker.io/$DOCKER_ACCOUNT_NAME/$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION"

# Controlla se un container con lo stesso nome è già in esecuzione
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Un container con il nome $CONTAINER_NAME è già in esecuzione."
    exit 1
fi

# Controlla se un container con lo stesso nome esiste (anche se fermo)
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    echo "Un container con il nome $CONTAINER_NAME esiste già. Rimuovilo prima di avviarne uno nuovo."
    exit 1
fi

# Esegui il container
docker run -d --runtime nvidia \
        --shm-size=5gb \
        --gpus 'all,"capabilities=compute,utility,graphics,video"'   \
	-p 2222:22 -p 5000:5000 -p 80:8080 -p 8888:8888 \
  	--env-file .env \
  	-v /home/crono/app:/app \
  	-v $(pwd)/.bashrc:/home/developer/.bashrc \
	-v $(pwd)/.bashrc:/root/.bashrc \
  	--mount type=tmpfs,destination=/mnt/hls \
	--name $CONTAINER_NAME $IMAGE_NAME 

# Verifica se il container è stato avviato correttamente
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Il container $CONTAINER_NAME è stato avviato correttamente."
    docker exec $CONTAINER_NAME /bin/bash
else
    echo "Errore nell'avvio del container $CONTAINER_NAME."
    exit 1
fi

