#!/bin/sh

SOURCE=sources/$1

PRODUCTION=flatmaps/production
STAGING=flatmaps/staging
REPO="git@github.com:AnatomicMaps/human-flatmap.git"

if [[ $1 = "male" || $1 = "female" ]]; then
    REPO=git@github.com:AnatomicMaps/human-flatmap.git
    MANIFEST=$SOURCE/$1.manifest.json
    MAP_PRODUCTION=$PRODUCTION/human-flatmap_$1
    MAP_STAGING=$STAGING/human-flatmap_$1
elif [[ $1 = "functional-connectivity" ]]; then
    REPO=git@github.com:AnatomicMaps/$1.git
    MANIFEST=$SOURCE/manifest.json
    MAP_PRODUCTION=$PRODUCTION/$1
    MAP_STAGING=$STAGING/$1
else
    REPO=git@github.com:AnatomicMaps/$1-flatmap.git
    MANIFEST=$SOURCE/manifest.json
    MAP_PRODUCTION=$PRODUCTION/$1-flatmap
    MAP_STAGING=$STAGING/$1-flatmap
fi

LOG_PRODUCTION=$PRODUCTION/$1.log
LOG_STAGING=$STAGING/$1.log
OUTPUT=results/$1.$2

IS_REFRESH=${3:-no}

if [[ $IS_REFRESH = "refresh" || ! -d "$SOURCE" || ! -d "$MAP_PRODUCTION" || ! -d "$MAP_STAGING" ]]; then
    
    if [[ -d "$SOURCE" ]]; then
        rm -rf $SOURCE
    fi
    if [[ -d "$MAP_PRODUCTION" ]]; then
        rm -rf $MAP_PRODUCTION
        rm $LOG_PRODUCTION
    fi
    if [[ -d "$MAP_STAGING" ]]; then
        rm -rf $MAP_STAGING
        rm $LOG_STAGING
    fi
    echo $REPO
    git clone $REPO $SOURCE

    cd mapmaker
    poetry run python runmaker.py --output ../$PRODUCTION --clean \
        --source ../$MANIFEST \
        --log ../$LOG_PRODUCTION \
        --ignore-git \
        --sckan-version production

    poetry run python runmaker.py --output ../$STAGING --clean \
        --source ../$MANIFEST \
        --log ../$LOG_STAGING \
        --ignore-git \
        --sckan-version staging

    cd ..

fi

poetry run python fcompare.py --production $MAP_PRODUCTION \
    --plog $LOG_PRODUCTION \
    --staging $MAP_STAGING \
    --slog $LOG_STAGING \
    --output $OUTPUT
