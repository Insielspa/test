#!/bin/bash

source .build-env
source .env

DOCKER_BASE_DIR=.
DOCKER_IMAGE_NAME=$BUILD_IMAGE_NAME

FVGVISION_AI_SCENARIO=main

# Variabile per la versione dell'immagine
DOCKER_IMAGE_VERSION=${BUILD_IMAGE_VERSION}-${BUILD_IMAGE_PLATFORM}${BUILD_IMAGE_PRODUCTION_PREFIX}

echo Effettuo run $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION


# Nome del container
CONTAINER_NAME="fvgvision-ai-main"

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
docker run -d                                                         \
        --shm-size=5gb                                                \
        --gpus 'all,"capabilities=compute,utility,graphics,video"'    \
        -p 5000:5000 -p 80:8080 -p 8081:8081                          \
  	    --env-file .env-$FVGVISION_AI_SCENARIO                        \
  	    -v $APP_PATH:/app                                             \
  	    -v $(pwd)/runtime/.bashrc:/home/developer/.bashrc             \
	      -v $(pwd)/runtime/.bashrc:/root/.bashrc                       \
  	    --mount type=tmpfs,destination=/mnt/hls                       \
	      --name $CONTAINER_NAME $IMAGE_NAME

# Verifica se il container è stato avviato correttamente
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Il container $CONTAINER_NAME è stato avviato correttamente."
    docker exec $CONTAINER_NAME /bin/bash
else
    echo "Errore nell'avvio del container $CONTAINER_NAME."
    exit 1
fi

