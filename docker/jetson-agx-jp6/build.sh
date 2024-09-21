#!/bin/bash
source .build-env
source .env

DOCKER_BASE_DIR=.
DOCKER_IMAGE_NAME=$BUILD_IMAGE_NAME

# Variabile per la versione dell'immagine
DOCKER_IMAGE_VERSION=${BUILD_IMAGE_VERSION}-${BUILD_IMAGE_PLATFORM}

echo "Effettuo build $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION"

DEPLOY=false
APP_OVERRIDE=false
BUILD_TYPE=""
APP_DIR="$APP_PATH"
ASSETS_DIR="../assets"

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help               Display this help message"
    echo "  --deploy                 Push the image to the registry"
    echo "  --dev                    Build the development image"
    echo "  --prod                   Build the production image"
    echo "  --app=<path>             Specify the application directory path (required for production)"
    exit 1
}

while getopts ":h-:" opt; do
    case $opt in
        -)
            case "${OPTARG}" in
                help)
                    usage
                    ;;
                deploy)
                    DEPLOY=true
                    ;;
                dev)
                    BUILD_TYPE="development"
                    ;;
                prod)
                    BUILD_TYPE="production"
                    ;;
                app=*)
                    APP_DIR="${OPTARG#*=}"
                    APP_OVERRIDE=true
                    ;;
                *)
                    echo "Invalid option: --$OPTARG"
                    usage
                    ;;
            esac
            ;;
        h)
            usage
            ;;
        *)
            echo "Invalid option: -$OPTARG"
            usage
            ;;
    esac
done

shift $((OPTIND -1))

# Controllo per garantire che non siano utilizzati parametri incompatibili
if [[ -z "$BUILD_TYPE" ]]; then
    echo "Devi specificare almeno uno dei seguenti parametri: --dev o --prod."
    exit 1
fi

if [[ "$BUILD_TYPE" == "development" && "$APP_OVERRIDE" = true ]]; then
    echo "L'opzione --app non può essere utilizzata con --dev."
    exit 1
fi

if [[ "$BUILD_TYPE" == "production" && -z "$APP_DIR" ]]; then
    echo "[$APP_DIR]Deve essere specificata la cartella dell'applicazione quando si utilizza --prod."
    exit 1
fi

# Creazione della cartella build all'interno della directory di lavoro
BUILD_DIR="$DOCKER_BASE_DIR/build"

# Controllo se la cartella build esiste già e, in caso affermativo, rimuoverla
if [ -d "$BUILD_DIR" ]; then
   echo "La cartella build esiste già. Verrà rimossa..."
   rm -rf "$BUILD_DIR"
fi
mkdir -p "$BUILD_DIR"

# Visualizzazione del percorso assoluto della cartella build
ABSOLUTE_BUILD_DIR=$(realpath "$BUILD_DIR")
echo "Il percorso assoluto della cartella di build è: $ABSOLUTE_BUILD_DIR"

echo "Copio la cartella assets in $BUILD_DIR/assets"
cp -r "$ASSETS_DIR" "$BUILD_DIR/assets"

if [[ "$BUILD_TYPE" == "production" ]]; then
    echo "Copio la cartella $APP_DIR in $BUILD_DIR/app"
    cp -r "$APP_DIR" "$BUILD_DIR/app"
    # Calcolo e visualizzazione della dimensione della cartella app
    if [ -d "$APP_DIR" ]; then
       APP_SIZE=$(du -sh "$APP_DIR" | cut -f1)
       echo "Dimensione della cartella app: $APP_SIZE"
      cp -r "$APP_DIR" "$BUILD_DIR/app"
    else
       echo "La cartella specificata in --app non esiste: $APP_DIR"
       exit 1
   fi
fi

# Aggiunta del suffisso alla versione dell'immagine
if [[ "$BUILD_TYPE" == "development" ]]; then
    DOCKER_IMAGE_VERSION="${DOCKER_IMAGE_VERSION}${BUILD_IMAGE_DEVELOPMENT_PREFIX}"
elif [[ "$BUILD_TYPE" == "production" ]]; then
    DOCKER_IMAGE_VERSION="${DOCKER_IMAGE_VERSION}${BUILD_IMAGE_PRODUCTION_PREFIX}"
fi

source .env

echo "Building $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION"
docker build --tag xcesco/$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION \
    --build-arg USER_ID=$USER_ID \
    --build-arg GROUP_ID=$GROUP_ID \
    --target $BUILD_TYPE -f $DOCKER_BASE_DIR/Dockerfile --load $DOCKER_BASE_DIR

 # Rimozione della cartella build
 #echo "Rimozione della cartella di build: $BUILD_DIR"
 #rm -rf "$BUILD_DIR"


if [ "$DEPLOY" = true ]; then
    echo "Pushing the image to the registry"
    docker push xcesco/$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION
fi
